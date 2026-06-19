from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Tenant, TenantFeature
from .serializers import TenantSerializer, TenantRegisterSerializer, TenantFeatureSerializer
from core.permissions import IsSuperAdmin


def _is_primary_super_admin(user):
    """
    Sirf Organization 1 (is_primary) ka super admin nayi organizations bana sakta hai.
    """
    return (
        user.is_super_admin
        and user.tenant_id is not None
        and getattr(user.tenant, "is_primary", False)
    )


class OrganizationCreateView(APIView):
    """
    Nayi organization banao. Sirf primary org (Org 1) ka super admin kar sakta hai.
    Yeh sirf organization banata hai — uske users baad mein add hote hain.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not _is_primary_super_admin(request.user):
            return Response(
                {"detail": "Only the primary Super Admin can create organizations."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = TenantRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant = serializer.save()
        TenantFeature.objects.get_or_create(tenant=tenant)
        return Response(TenantSerializer(tenant).data, status=status.HTTP_201_CREATED)


class TenantDetailView(APIView):
    """Current logged-in user ki apni organization."""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"detail": "No organization."}, status=404)
        return Response(TenantSerializer(tenant).data)

    def patch(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"detail": "No organization."}, status=404)
        if not request.user.is_super_admin:
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TenantSerializer(tenant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SuperAdminStatsView(APIView):
    permission_classes = (IsSuperAdmin,)

    def get(self, request):
        total = Tenant.objects.count()
        by_status = dict(
            Tenant.objects.values_list("status")
            .annotate(c=Count("id"))
            .values_list("status", "c")
        )
        by_plan = dict(
            Tenant.objects.values_list("plan")
            .annotate(c=Count("id"))
            .values_list("plan", "c")
        )
        return Response({
            "total_tenants": total,
            "by_status": by_status,
            "by_plan": by_plan,
        })


class SuperAdminTenantListView(APIView):
    permission_classes = (IsSuperAdmin,)

    def get(self, request):
        tenants = Tenant.objects.select_related("features").all()
        return Response(TenantSerializer(tenants, many=True).data)


class SuperAdminTenantDetailView(APIView):
    permission_classes = (IsSuperAdmin,)

    def get(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, id=tenant_id)
        return Response(TenantSerializer(tenant).data)

    def patch(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, id=tenant_id)
        serializer = TenantSerializer(tenant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TenantSerializer(tenant).data)


class SuperAdminFeatureFlagView(APIView):
    """Super Admin se kisi organization ke feature flags update karo."""
    permission_classes = (IsSuperAdmin,)

    def get(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, id=tenant_id)
        features, _ = TenantFeature.objects.get_or_create(tenant=tenant)
        return Response(TenantFeatureSerializer(features).data)

    def patch(self, request, tenant_id):
        tenant = get_object_or_404(Tenant, id=tenant_id)
        features, _ = TenantFeature.objects.get_or_create(tenant=tenant)
        serializer = TenantFeatureSerializer(features, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
