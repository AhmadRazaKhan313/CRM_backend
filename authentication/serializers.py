from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        data["user"] = user
        return data


class TenantMiniSerializer(serializers.Serializer):
    """
    Login response mein tenant + feature flags include karne ke liye.
    Sirf jo frontend ko chahiye woh fields.
    """
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    plan = serializers.CharField()
    status = serializers.CharField()
    features = serializers.SerializerMethodField()

    def get_features(self, tenant):
        try:
            f = tenant.features
            return {
                "hrms": f.hrms,
                "analytics": f.analytics,
                "ai_assistant": f.ai_assistant,
                "multi_department": f.multi_department,
                "custom_branding": f.custom_branding,
                "api_access": f.api_access,
            }
        except Exception:
            return {}


class UserSerializer(serializers.ModelSerializer):
    # ✅ Login response mein tenant + features bhi aayega
    tenant = TenantMiniSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "email", "full_name", "role", "department",
            "employee_id", "avatar", "phone",
            "is_super_admin", "tenant",
        )
        read_only_fields = ("id", "employee_id", "is_super_admin", "tenant")


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("email", "full_name", "role", "department", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
