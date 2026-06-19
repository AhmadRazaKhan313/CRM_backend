from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Department
from .serializers import DepartmentSerializer
from core.permissions import IsAuthenticatedInTenant, HasPermission, FeatureRequired

FEATURE = FeatureRequired("departments_module")


class DepartmentListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("departments.create")()]
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("departments.view")()]

    def get(self, request):
        qs = Department.objects.filter(
            tenant=request.user.tenant,
            is_active=True
        ).select_related("head")
        return Response(DepartmentSerializer(qs, many=True).data)

    def post(self, request):
        # Prevent duplicate department with same name
        name = (request.data.get("name") or "").strip()
        if Department.objects.filter(
            tenant=request.user.tenant,
            name__iexact=name,
            is_active=True,
        ).exists():
            return Response(
                {"detail": f"A department named '{name}' already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=request.user.tenant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DepartmentDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("departments.delete")()]
        if self.request.method == "PATCH":
            return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("departments.edit")()]
        return [IsAuthenticatedInTenant(), FEATURE(), HasPermission("departments.view")()]

    def get(self, request, pk):
        dept = get_object_or_404(Department, pk=pk, tenant=request.user.tenant)
        return Response(DepartmentSerializer(dept).data)

    def patch(self, request, pk):
        dept = get_object_or_404(Department, pk=pk, tenant=request.user.tenant)
        serializer = DepartmentSerializer(dept, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        dept = get_object_or_404(Department, pk=pk, tenant=request.user.tenant)
        dept.is_active = False
        dept.head      = None
        dept.save()
        return Response(
            {"detail": f"Department '{dept.name}' has been deactivated."},
            status=status.HTTP_200_OK
        )
