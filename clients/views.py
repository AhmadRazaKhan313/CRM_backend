from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Client, Payment, ClientFile
from .serializers import (
    ClientListSerializer, ClientDetailSerializer,
    ClientCreateSerializer, PaymentSerializer, ClientFileSerializer
)
from core.permissions import IsAnyEmployee, IsManagerOrAbove


class ClientListCreateView(APIView):
    permission_classes = (IsAnyEmployee,)

    def get(self, request):
        qs = Client.objects.filter(
            tenant=request.user.tenant,
            is_archived=False
        ).select_related("assigned_to", "created_by")

        dept = request.query_params.get("department")
        status_f = request.query_params.get("status")
        tag = request.query_params.get("tag")
        search = request.query_params.get("search")

        if dept:
            qs = qs.filter(department=dept)
        if status_f:
            qs = qs.filter(status=status_f)
        if tag:
            qs = qs.filter(tag=tag)
        if search:
            qs = qs.filter(full_name__icontains=search) | qs.filter(email__icontains=search)

        if request.user.is_super_admin or request.user.role in ("ceo", "coo", "sales_director"):
            return Response(ClientListSerializer(qs, many=True).data)

        if request.user.role in ("dept_head", "lead_manager", "sales_manager"):
            qs = qs.filter(department=request.user.department)

        if request.user.role in ("lead_employee", "sales_employee"):
            qs = qs.filter(assigned_to=request.user)

        return Response(ClientListSerializer(qs, many=True).data)

    def post(self, request):
        serializer = ClientCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        client = serializer.save()
        return Response(ClientDetailSerializer(client).data, status=status.HTTP_201_CREATED)


class ClientDetailView(APIView):
    permission_classes = (IsAnyEmployee,)

    def _get_client(self, pk, user):
        return get_object_or_404(Client, pk=pk, tenant=user.tenant, is_archived=False)

    def get(self, request, pk):
        client = self._get_client(pk, request.user)
        return Response(ClientDetailSerializer(client).data)

    def patch(self, request, pk):
        client = self._get_client(pk, request.user)
        for attr, val in request.data.items():
            setattr(client, attr, val)
        client.save()
        return Response(ClientDetailSerializer(client).data)

    def delete(self, request, pk):
        client = self._get_client(pk, request.user)
        client.is_archived = True
        client.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientPaymentView(APIView):
    permission_classes = (IsManagerOrAbove,)

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk, tenant=request.user.tenant)
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(
            client=client,
            tenant=request.user.tenant
        )
        if payment.status == "paid":
            payment.paid_at = timezone.now()
            payment.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, client__tenant=request.user.tenant)
        for attr, val in request.data.items():
            setattr(payment, attr, val)
        if request.data.get("status") == "paid" and not payment.paid_at:
            payment.paid_at = timezone.now()
        payment.save()
        return Response(PaymentSerializer(payment).data)


class ClientFileView(APIView):
    permission_classes = (IsAnyEmployee,)

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk, tenant=request.user.tenant)
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        cf = ClientFile.objects.create(
            client=client,
            file=file,
            name=file.name,
            uploaded_by=request.user
        )
        return Response(ClientFileSerializer(cf).data, status=status.HTTP_201_CREATED)