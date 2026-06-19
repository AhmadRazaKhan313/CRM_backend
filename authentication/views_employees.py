from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import User
from .serializers_employees import (
    EmployeeListSerializer,
    EmployeeCreateSerializer,
    EmployeeUpdateSerializer,
)
from core.permissions import HasPermission, IsAuthenticatedInTenant
from core.models import UserRole, Role


class EmployeeListCreateView(APIView):
    """
    Employees apni hi organization ke andar.
    View ke liye employees.view, create ke liye employees.create permission chahiye.
    """
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedInTenant(), HasPermission("employees.create")()]
        return [IsAuthenticatedInTenant(), HasPermission("employees.view")()]

    def get(self, request):
        qs = User.objects.filter(
            tenant=request.user.tenant,
            is_super_admin=False,
        ).prefetch_related("assigned_roles__role")

        department = request.query_params.get("department")
        search     = request.query_params.get("search")
        if department:
            qs = qs.filter(department=department)
        if search:
            qs = qs.filter(full_name__icontains=search) | qs.filter(email__icontains=search)

        return Response(EmployeeListSerializer(qs, many=True).data)

    def post(self, request):
        serializer = EmployeeCreateSerializer(
            data=request.data,
            context={"request": request, "tenant": request.user.tenant},
        )
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        return Response(EmployeeListSerializer(employee).data, status=status.HTTP_201_CREATED)


class EmployeeDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticatedInTenant(), HasPermission("employees.delete")()]
        if self.request.method == "PATCH":
            return [IsAuthenticatedInTenant(), HasPermission("employees.edit")()]
        return [IsAuthenticatedInTenant(), HasPermission("employees.view")()]

    def _get_employee(self, pk, tenant):
        return get_object_or_404(User, pk=pk, tenant=tenant, is_super_admin=False)

    def get(self, request, pk):
        emp = self._get_employee(pk, request.user.tenant)
        return Response(EmployeeListSerializer(emp).data)

    def patch(self, request, pk):
        emp        = self._get_employee(pk, request.user.tenant)
        serializer = EmployeeUpdateSerializer(emp, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        emp.refresh_from_db()
        return Response(EmployeeListSerializer(emp).data)

    def delete(self, request, pk):
        emp = self._get_employee(pk, request.user.tenant)
        emp.is_active = False
        emp.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeRoleAssignView(APIView):
    """Employee ko custom role assign/remove karna."""
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), HasPermission("employees.edit")()]

    def post(self, request, pk):
        emp     = get_object_or_404(User, pk=pk, tenant=request.user.tenant)
        role_id = request.data.get("role_id")
        role    = get_object_or_404(Role, pk=role_id, tenant=request.user.tenant)
        user_role, created = UserRole.objects.get_or_create(
            user=emp, role=role,
            defaults={"assigned_by": request.user},
        )
        if not created:
            return Response({"detail": "Role already assigned."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Role assigned successfully."}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        emp     = get_object_or_404(User, pk=pk, tenant=request.user.tenant)
        role_id = request.data.get("role_id")
        # Last role nahi hatne dena — har user ke paas kam se kam ek role ho
        if emp.assigned_roles.count() <= 1:
            return Response(
                {"detail": "Cannot remove the last role. A user must have at least one role."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        UserRole.objects.filter(user=emp, role_id=role_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminPasswordResetView(APIView):
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), HasPermission("employees.edit")()]

    def post(self, request, pk):
        emp          = get_object_or_404(User, pk=pk, tenant=request.user.tenant, is_super_admin=False)
        new_password = request.data.get("new_password", "")
        if len(new_password) < 8:
            return Response(
                {"detail": "Password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        emp.set_password(new_password)
        emp.save()
        return Response({"detail": f"Password reset successfully for {emp.full_name}."})
