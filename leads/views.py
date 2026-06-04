from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Lead, LeadActivity
from .serializers import (
    LeadListSerializer, LeadDetailSerializer,
    LeadCreateSerializer, LeadActivitySerializer
)
from core.permissions import IsManagerOrAbove, IsAnyEmployee


class LeadListCreateView(APIView):
    permission_classes = (IsAnyEmployee,)

    def get(self, request):
        qs = Lead.objects.filter(
            tenant=request.user.tenant,
            is_archived=False
        ).select_related("assigned_to", "created_by")

        # filters
        status_f = request.query_params.get("status")
        dept_f = request.query_params.get("department")
        source_f = request.query_params.get("source")
        search = request.query_params.get("search")

        if status_f:
            qs = qs.filter(status=status_f)
        if dept_f:
            qs = qs.filter(department=dept_f)
        if source_f:
            qs = qs.filter(source=source_f)
        if search:
            qs = qs.filter(full_name__icontains=search) | qs.filter(email__icontains=search)

        # employees sirf apne leads dekhein
        if request.user.role in ("lead_employee", "sales_employee"):
            qs = qs.filter(assigned_to=request.user)

        # dept isolation
        if request.user.role in ("lead_manager", "sales_manager", "dept_head"):
            qs = qs.filter(department=request.user.department)

        return Response(LeadListSerializer(qs, many=True).data)

    def post(self, request):
        serializer = LeadCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        lead = serializer.save()
        return Response(LeadDetailSerializer(lead).data, status=status.HTTP_201_CREATED)


class LeadDetailView(APIView):
    permission_classes = (IsAnyEmployee,)

    def _get_lead(self, pk, user):
        lead = get_object_or_404(Lead, pk=pk, tenant=user.tenant, is_archived=False)
        if user.role in ("lead_employee", "sales_employee"):
            if lead.assigned_to != user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied()
        return lead

    def get(self, request, pk):
        lead = self._get_lead(pk, request.user)
        return Response(LeadDetailSerializer(lead).data)

    def patch(self, request, pk):
        lead = self._get_lead(pk, request.user)
        old_status = lead.status
        for attr, val in request.data.items():
            setattr(lead, attr, val)
        lead.save()
        if "status" in request.data and request.data["status"] != old_status:
            LeadActivity.objects.create(
                lead=lead,
                activity_type="status_change",
                note=f"Status changed from {old_status} to {lead.status}",
                created_by=request.user
            )
        return Response(LeadDetailSerializer(lead).data)

    def delete(self, request, pk):
        lead = self._get_lead(pk, request.user)
        lead.is_archived = True
        lead.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeadAssignView(APIView):
    permission_classes = (IsManagerOrAbove,)

    def post(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk, tenant=request.user.tenant)
        user_id = request.data.get("user_id")
        from authentication.models import User
        employee = get_object_or_404(User, pk=user_id, tenant=request.user.tenant)
        lead.assigned_to = employee
        lead.save()
        LeadActivity.objects.create(
            lead=lead,
            activity_type="note",
            note=f"Lead assigned to {employee.full_name}",
            created_by=request.user
        )
        return Response(LeadDetailSerializer(lead).data)


class LeadActivityView(APIView):
    permission_classes = (IsAnyEmployee,)

    def post(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk, tenant=request.user.tenant)
        activity = LeadActivity.objects.create(
            lead=lead,
            activity_type=request.data.get("activity_type", "note"),
            note=request.data.get("note", ""),
            created_by=request.user
        )
        return Response(LeadActivitySerializer(activity).data, status=status.HTTP_201_CREATED)