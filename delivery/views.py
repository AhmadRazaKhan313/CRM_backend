from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Delivery, Milestone
from .serializers import (
    DeliveryListSerializer, DeliveryDetailSerializer,
    DeliveryCreateSerializer, MilestoneSerializer,
)
from core.permissions import (
    IsAuthenticatedInTenant, HasPermission, FeatureRequired, user_has_permission,
)

FEATURE = FeatureRequired("delivery_module")

DELIVERY_PATCH_ALLOWED = {
    "title", "description", "department", "status", "progress",
    "assigned_to", "start_date", "due_date", "delivery_link", "notes",
}


class DeliveryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("delivery.create")()]
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("delivery.view")()]

    def get(self, request):
        qs = Delivery.objects.filter(
            tenant=request.user.tenant,
            is_archived=False
        ).select_related("client", "assigned_to").prefetch_related("milestones")

        status_f = request.query_params.get("status")
        client_f = request.query_params.get("client")
        if status_f: qs = qs.filter(status=status_f)
        if client_f: qs = qs.filter(client_id=client_f)

        if not (request.user.is_super_admin or user_has_permission(request.user, "delivery.view_all")):
            qs = qs.filter(assigned_to=request.user)

        return Response(DeliveryListSerializer(qs, many=True).data)

    def post(self, request):
        serializer = DeliveryCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        delivery = serializer.save()
        return Response(DeliveryDetailSerializer(delivery).data, status=status.HTTP_201_CREATED)


class DeliveryDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("delivery.delete")()]
        if self.request.method == "PATCH":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("delivery.edit")()]
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("delivery.view")()]

    def _get(self, pk, user):
        return get_object_or_404(Delivery, pk=pk, tenant=user.tenant, is_archived=False)

    def get(self, request, pk):
        return Response(DeliveryDetailSerializer(self._get(pk, request.user)).data)

    def patch(self, request, pk):
        delivery  = self._get(pk, request.user)
        safe_data = {k: v for k, v in request.data.items() if k in DELIVERY_PATCH_ALLOWED}
        serializer = DeliveryCreateSerializer(
            delivery, data=safe_data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        delivery = serializer.save()

        # Status delivered hone par timestamp set karo
        if safe_data.get("status") == "delivered" and not delivery.delivered_at:
            delivery.delivered_at = timezone.now()
            delivery.save()

        return Response(DeliveryDetailSerializer(delivery).data)

    def delete(self, request, pk):
        delivery = self._get(pk, request.user)
        delivery.is_archived = True
        delivery.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MilestoneView(APIView):
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("delivery.edit")()]

    def post(self, request, pk):
        delivery  = get_object_or_404(Delivery, pk=pk, tenant=request.user.tenant)
        milestone = Milestone.objects.create(
            delivery = delivery,
            title    = request.data.get("title", ""),
            due_date = request.data.get("due_date") or None,
        )
        self._recalc_progress(delivery)
        return Response(MilestoneSerializer(milestone).data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        milestone = get_object_or_404(Milestone, pk=pk, delivery__tenant=request.user.tenant)
        milestone.is_done = request.data.get("is_done", milestone.is_done)
        milestone.save()
        self._recalc_progress(milestone.delivery)
        return Response(MilestoneSerializer(milestone).data)

    def delete(self, request, pk):
        milestone = get_object_or_404(Milestone, pk=pk, delivery__tenant=request.user.tenant)
        delivery  = milestone.delivery
        milestone.delete()
        self._recalc_progress(delivery)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _recalc_progress(self, delivery):
        total = delivery.milestones.count()
        if total == 0:
            return
        done = delivery.milestones.filter(is_done=True).count()
        delivery.progress = int((done / total) * 100)
        delivery.save(update_fields=["progress"])
