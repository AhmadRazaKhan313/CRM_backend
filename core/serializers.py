from rest_framework import serializers
from .models import Permission, Role, UserRole


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Permission
        fields = ("id", "module", "action", "codename", "label")


class RoleSerializer(serializers.ModelSerializer):
    permissions    = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True,
        queryset=Permission.objects.all(),
        source="permissions",
        required=False,
    )
    user_count = serializers.SerializerMethodField()

    class Meta:
        model  = Role
        fields = (
            "id", "name", "description",
            "permissions", "permission_ids",
            "user_count", "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_user_count(self, obj):
        return obj.assigned_users.count()


class UserRoleSerializer(serializers.ModelSerializer):
    role_name        = serializers.CharField(source="role.name",             read_only=True)
    assigned_by_name = serializers.CharField(source="assigned_by.full_name", read_only=True)

    class Meta:
        model  = UserRole
        fields = ("id", "role", "role_name", "assigned_by_name", "assigned_at")
