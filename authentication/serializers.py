from rest_framework import serializers
from .models import User
from core.permissions import user_permission_codenames


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("Account is disabled.")
        data["user"] = user
        return data


class TenantMiniSerializer(serializers.Serializer):
    id         = serializers.IntegerField()
    name       = serializers.CharField()
    slug       = serializers.CharField()
    plan       = serializers.CharField()
    status     = serializers.CharField()
    is_primary = serializers.BooleanField()
    features   = serializers.SerializerMethodField()

    def get_features(self, tenant):
        try:
            f = tenant.features
            return {
                "leads_module":       f.leads_module,
                "clients_module":     f.clients_module,
                "tasks_module":       f.tasks_module,
                "reports_module":     f.reports_module,
                "departments_module": f.departments_module,
                "finance_module":     f.finance_module,
                "delivery_module":    f.delivery_module,
                "analytics":          f.analytics,
                "hrms":               f.hrms,
                "ai_assistant":       f.ai_assistant,
                "multi_department":   f.multi_department,
                "custom_branding":    f.custom_branding,
                "api_access":         f.api_access,
            }
        except Exception:
            return {}


class UserSerializer(serializers.ModelSerializer):
    tenant      = TenantMiniSerializer(read_only=True)
    roles       = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = (
            "id", "email", "full_name", "employee_id",
            "avatar", "phone", "is_super_admin",
            "tenant", "roles", "permissions",
        )
        read_only_fields = ("id", "employee_id", "is_super_admin", "tenant")

    def get_roles(self, obj):
        return obj.role_names

    def get_permissions(self, obj):
        # Frontend isi se dashboard aur sidebar dynamically banata hai
        return sorted(user_permission_codenames(obj))
