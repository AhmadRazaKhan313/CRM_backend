from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Department
from .serializers import DepartmentSerializer
from core.permissions import IsCEOOrAbove, IsDeptHeadOrAbove


class DepartmentListCreateView(APIView):
    permission_classes = (IsDeptHeadOrAbove,)

    def get(self, request):
        qs = Department.objects.filter(
            tenant=request.user.tenant,
            is_active=True
        ).select_related("head")
        return Response(DepartmentSerializer(qs, many=True).data)

    def post(self, request):
        if not request.user.role in ("ceo", "coo"):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        serializer = DepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tenant=request.user.tenant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DepartmentDetailView(APIView):
    permission_classes = (IsDeptHeadOrAbove,)

    def get(self, request, pk):
        dept = get_object_or_404(Department, pk=pk, tenant=request.user.tenant)
        return Response(DepartmentSerializer(dept).data)

    def patch(self, request, pk):
        if not request.user.role in ("ceo", "coo"):
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)
        dept = get_object_or_404(Department, pk=pk, tenant=request.user.tenant)
        serializer = DepartmentSerializer(dept, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)