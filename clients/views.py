from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Client, SalesDetail, TechDetail, SEODetail, Payment, ClientFile
from .serializers import (
    ClientListSerializer, ClientDetailSerializer,
    ClientCreateSerializer, PaymentSerializer, ClientFileSerializer,
    SalesDetailSerializer, TechDetailSerializer, SEODetailSerializer,
)
from core.permissions import (
    IsAuthenticatedInTenant, HasPermission, FeatureRequired, user_has_permission,
)
from notifications.utils import notify

FEATURE = FeatureRequired("clients_module")

CLIENT_PATCH_ALLOWED = {
    "full_name", "email", "phone", "country", "company",
    "department", "status", "tag", "notes", "assigned_to",
}

PAYMENT_PATCH_ALLOWED = {
    "amount", "paid_amount", "status", "method", "due_date", "notes",
}


# ─── Client List / Create ─────────────────────────────────────

class ClientListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("clients.create")()]
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("clients.view")()]

    def get(self, request):
        qs = Client.objects.filter(
            tenant=request.user.tenant,
            is_archived=False
        ).select_related("assigned_to", "created_by", "converted_from")

        dept     = request.query_params.get("department")
        status_f = request.query_params.get("status")
        tag      = request.query_params.get("tag")
        search   = request.query_params.get("search")

        if dept:     qs = qs.filter(department=dept)
        if status_f: qs = qs.filter(status=status_f)
        if tag:      qs = qs.filter(tag=tag)
        if search:
            qs = (
                qs.filter(full_name__icontains=search) |
                qs.filter(email__icontains=search) |
                qs.filter(company__icontains=search)
            )

        if not (request.user.is_super_admin or user_has_permission(request.user, "clients.view_all")):
            qs = qs.filter(assigned_to=request.user)

        return Response(ClientListSerializer(qs, many=True).data)

    def post(self, request):
        serializer = ClientCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        client = serializer.save()
        return Response(ClientDetailSerializer(client).data, status=status.HTTP_201_CREATED)


# ─── Client Detail ────────────────────────────────────────────

class ClientDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("clients.delete")()]
        if self.request.method == "PATCH":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("clients.edit")()]
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("clients.view")()]

    def _get_client(self, pk, user):
        client = get_object_or_404(Client, pk=pk, tenant=user.tenant, is_archived=False)
        if not (user.is_super_admin or user_has_permission(user, "clients.view_all")):
            if client.assigned_to != user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied()
        return client

    def get(self, request, pk):
        return Response(ClientDetailSerializer(self._get_client(pk, request.user)).data)

    def patch(self, request, pk):
        client    = self._get_client(pk, request.user)
        safe_data = {k: v for k, v in request.data.items() if k in CLIENT_PATCH_ALLOWED}
        serializer = ClientCreateSerializer(
            client, data=safe_data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        client.refresh_from_db()
        return Response(ClientDetailSerializer(client).data)

    def delete(self, request, pk):
        client = self._get_client(pk, request.user)
        client.is_archived = True
        client.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ─── Department Detail Views ──────────────────────────────────

class ClientSalesDetailView(APIView):
    """
    GET  /api/clients/<pk>/sales-detail/  — detail dekho
    POST /api/clients/<pk>/sales-detail/  — create ya update
    """
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("clients.edit")()]

    def _get_client(self, pk, user):
        return get_object_or_404(Client, pk=pk, tenant=user.tenant, is_archived=False)

    def get(self, request, pk):
        client = self._get_client(pk, request.user)
        try:
            return Response(SalesDetailSerializer(client.sales_detail).data)
        except SalesDetail.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    def post(self, request, pk):
        client = self._get_client(pk, request.user)
        try:
            instance = client.sales_detail
            serializer = SalesDetailSerializer(instance, data=request.data, partial=True)
        except SalesDetail.DoesNotExist:
            serializer = SalesDetailSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(client=client)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientTechDetailView(APIView):
    """
    GET  /api/clients/<pk>/tech-detail/
    POST /api/clients/<pk>/tech-detail/
    """
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("clients.edit")()]

    def _get_client(self, pk, user):
        return get_object_or_404(Client, pk=pk, tenant=user.tenant, is_archived=False)

    def get(self, request, pk):
        client = self._get_client(pk, request.user)
        try:
            return Response(TechDetailSerializer(client.tech_detail).data)
        except TechDetail.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    def post(self, request, pk):
        client = self._get_client(pk, request.user)
        try:
            instance   = client.tech_detail
            serializer = TechDetailSerializer(instance, data=request.data, partial=True)
        except TechDetail.DoesNotExist:
            serializer = TechDetailSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(client=client)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientSEODetailView(APIView):
    """
    GET  /api/clients/<pk>/seo-detail/
    POST /api/clients/<pk>/seo-detail/
    """
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("clients.edit")()]

    def _get_client(self, pk, user):
        return get_object_or_404(Client, pk=pk, tenant=user.tenant, is_archived=False)

    def get(self, request, pk):
        client = self._get_client(pk, request.user)
        try:
            return Response(SEODetailSerializer(client.seo_detail).data)
        except SEODetail.DoesNotExist:
            return Response({}, status=status.HTTP_200_OK)

    def post(self, request, pk):
        client = self._get_client(pk, request.user)
        try:
            instance   = client.seo_detail
            serializer = SEODetailSerializer(instance, data=request.data, partial=True)
        except SEODetail.DoesNotExist:
            serializer = SEODetailSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(client=client)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ─── Payments ─────────────────────────────────────────────────

class ClientPaymentView(APIView):
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("clients.edit")()]

    def get(self, request, pk):
        client   = get_object_or_404(Client, pk=pk, tenant=request.user.tenant)
        payments = client.payments.all()
        return Response(PaymentSerializer(payments, many=True).data)

    def post(self, request, pk):
        client     = get_object_or_404(Client, pk=pk, tenant=request.user.tenant)
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(client=client, tenant=request.user.tenant)
        if payment.status == "paid":
            payment.paid_at = timezone.now()
            payment.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        payment   = get_object_or_404(Payment, pk=pk, client__tenant=request.user.tenant)
        safe_data = {k: v for k, v in request.data.items() if k in PAYMENT_PATCH_ALLOWED}
        serializer = PaymentSerializer(payment, data=safe_data, partial=True)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        if safe_data.get("status") == "paid" and not payment.paid_at:
            payment.paid_at = timezone.now()
            payment.save()
        return Response(PaymentSerializer(payment).data)


# ─── Files ────────────────────────────────────────────────────

class ClientFileView(APIView):
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("clients.edit")()]

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk, tenant=request.user.tenant)
        file   = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        cf = ClientFile.objects.create(
            client=client, file=file,
            name=file.name, uploaded_by=request.user
        )
        return Response(ClientFileSerializer(cf).data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        cf = get_object_or_404(ClientFile, pk=pk, client__tenant=request.user.tenant)
        cf.file.delete(save=False)
        cf.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)