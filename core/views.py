from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Permission, Role, UserRole
from .serializers import PermissionSerializer, RoleSerializer, UserRoleSerializer
from .permissions import IsAuthenticatedInTenant, HasPermission


class PermissionListView(APIView):
    """Saari available permissions — role banate waqt inme se choose karte hain."""
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), HasPermission("roles.view")()]

    def get(self, request):
        perms  = Permission.objects.all()
        module = request.query_params.get("module")
        if module:
            perms = perms.filter(module=module)
        return Response(PermissionSerializer(perms, many=True).data)


class RoleListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticatedInTenant(), HasPermission("roles.create")()]
        return [IsAuthenticatedInTenant(), HasPermission("roles.view")()]

    def get(self, request):
        roles = Role.objects.filter(
            tenant=request.user.tenant
        ).prefetch_related("permissions").order_by("name")
        return Response(RoleSerializer(roles, many=True).data)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=request.user.tenant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RoleDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticatedInTenant(), HasPermission("roles.delete")()]
        if self.request.method == "PATCH":
            return [IsAuthenticatedInTenant(), HasPermission("roles.edit")()]
        return [IsAuthenticatedInTenant(), HasPermission("roles.view")()]

    def _get_role(self, pk, tenant):
        return get_object_or_404(Role, pk=pk, tenant=tenant)

    def get(self, request, pk):
        return Response(RoleSerializer(self._get_role(pk, request.user.tenant)).data)

    def patch(self, request, pk):
        role       = self._get_role(pk, request.user.tenant)
        serializer = RoleSerializer(role, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        role = self._get_role(pk, request.user.tenant)
        if role.assigned_users.exists():
            return Response(
                {"detail": "Cannot delete a role that is assigned to users."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRolesView(APIView):
    def get_permissions(self):
        return [IsAuthenticatedInTenant(), HasPermission("employees.view")()]

    def get(self, request, user_id):
        roles = UserRole.objects.filter(
            user_id=user_id,
            user__tenant=request.user.tenant,
        ).select_related("role", "user")
        return Response(UserRoleSerializer(roles, many=True).data)
