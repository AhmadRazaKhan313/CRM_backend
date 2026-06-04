from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .models import Tenant
from .serializers import TenantSerializer, TenantRegisterSerializer
from authentication.serializers import RegisterSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class TenantRegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        t_serializer = TenantRegisterSerializer(data=request.data)
        t_serializer.is_valid(raise_exception=True)
        tenant = t_serializer.save()

        user_data = {
            "email": request.data.get("email"),
            "full_name": request.data.get("admin_name", "Admin"),
            "password": request.data.get("password"),
            "role": "ceo",
        }
        u_serializer = RegisterSerializer(data=user_data)
        u_serializer.is_valid(raise_exception=True)
        user = u_serializer.save()
        user.tenant = tenant
        user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "tenant": TenantSerializer(tenant).data,
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_201_CREATED)


class TenantDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"detail": "No tenant."}, status=404)
        return Response(TenantSerializer(tenant).data)

    def patch(self, request):
        tenant = request.user.tenant
        if not tenant:
            return Response({"detail": "No tenant."}, status=404)
        serializer = TenantSerializer(tenant, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)