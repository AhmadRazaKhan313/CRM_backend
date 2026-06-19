from rest_framework import serializers
from .models import User
from core.models import Role, UserRole


class EmployeeListSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = (
            "id", "full_name", "email", "phone",
            "employee_id", "avatar", "is_active",
            "created_at", "roles",
        )

    def get_roles(self, obj):
        return list(
            obj.assigned_roles.select_related("role")
            .values_list("role__name", flat=True)
        )


class EmployeeCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Role.objects.all(),
        required=True,   # Role ab zaroori hai — koi user bina role ke nahi
    )

    class Meta:
        model  = User
        fields = ("full_name", "email", "phone", "password", "avatar", "role_ids")

    def validate_role_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one role is required.")
        tenant = self.context["tenant"]
        # Saari roles isi organization ki honi chahiye
        for role in value:
            if role.tenant_id != tenant.id:
                raise serializers.ValidationError(
                    "Roles must belong to your organization."
                )
        return value

    def create(self, validated_data):
        role_ids = validated_data.pop("role_ids", [])
        tenant   = self.context["tenant"]
        user = User.objects.create_user(**validated_data)
        user.tenant = tenant
        user.save()
        for role in role_ids:
            UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=self.context["request"].user,
            )
        return user


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ("full_name", "phone", "avatar", "is_active")
