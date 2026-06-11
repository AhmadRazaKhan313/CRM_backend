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
from core.permissions import IsAnyEmployee, IsManagerOrAbove, FeatureRequired

FEATURE = FeatureRequired("clients_module")

# ✅ FIX: Sirf yeh fields update ho sakti hain
CLIENT_PATCH_ALLOWED = {
    "full_name", "email", "phone", "country", "company",
    "department", "status", "tag", "notes", "assigned_to",
}

PAYMENT_PATCH_ALLOWED = {
    "amount", "paid_amount", "status", "method", "due_date", "notes",
}


class ClientListCreateView(APIView):
    permission_classes = (IsAnyEmployee, FEATURE)

    def get(self, request):
        qs = Client.objects.filter(
            tenant=request.user.tenant,
            is_archived=False
        ).select_related("assigned_to", "created_by")

        dept     = request.query_params.get("department")
        status_f = request.query_params.get("status")
        tag      = request.query_params.get("tag")
        search   = request.query_params.get("search")

        if dept:     qs = qs.filter(department=dept)
        if status_f: qs = qs.filter(status=status_f)
        if tag:      qs = qs.filter(tag=tag)
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
    permission_classes = (IsAnyEmployee, FEATURE)

    def _get_client(self, pk, user):
        client = get_object_or_404(Client, pk=pk, tenant=user.tenant, is_archived=False)
        # ✅ FIX: Employee sirf apne assigned clients access kar sake
        if user.role in ("lead_employee", "sales_employee"):
            if client.assigned_to != user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied()
        return client

    def get(self, request, pk):
        return Response(ClientDetailSerializer(self._get_client(pk, request.user)).data)

    def patch(self, request, pk):
        client = self._get_client(pk, request.user)
        # ✅ FIX: setattr hataya — whitelist se safe update
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


class ClientPaymentView(APIView):
    permission_classes = (IsManagerOrAbove, FEATURE)

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk, tenant=request.user.tenant)
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(client=client, tenant=request.user.tenant)
        if payment.status == "paid":
            payment.paid_at = timezone.now()
            payment.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, client__tenant=request.user.tenant)
        # ✅ FIX: setattr hataya — whitelist se safe update
        safe_data = {k: v for k, v in request.data.items() if k in PAYMENT_PATCH_ALLOWED}
        serializer = PaymentSerializer(payment, data=safe_data, partial=True)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        if safe_data.get("status") == "paid" and not payment.paid_at:
            payment.paid_at = timezone.now()
            payment.save()
        return Response(PaymentSerializer(payment).data)


class ClientFileView(APIView):
    permission_classes = (IsAnyEmployee, FEATURE)

    def post(self, request, pk):
        client = get_object_or_404(Client, pk=pk, tenant=request.user.tenant)
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        cf = ClientFile.objects.create(
            client=client, file=file,
            name=file.name, uploaded_by=request.user
        )
        return Response(ClientFileSerializer(cf).data, status=status.HTTP_201_CREATED)