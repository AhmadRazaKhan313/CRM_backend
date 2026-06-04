from rest_framework import serializers
from .models import Permission, Role, UserRole
from authentication.models import User


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "module", "action", "codename", "label")


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Permission.objects.all(),
        source="permissions"
    )
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            "id", "name", "description", "permissions",
            "permission_ids", "is_system", "user_count", "created_at"
        )
        read_only_fields = ("id", "is_system", "created_at")

    def get_user_count(self, obj):
        return obj.assigned_users.count()

    def create(self, validated_data):
        permissions = validated_data.pop("permissions", [])
        role = Role.objects.create(**validated_data)
        role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
        permissions = validated_data.pop("permissions", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        if permissions is not None:
            instance.permissions.set(permissions)
        return instance


class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()

    def validate(self, data):
        request = self.context["request"]
        try:
            user = User.objects.get(pk=data["user_id"], tenant=request.user.tenant)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found in your tenant.")
        try:
            role = Role.objects.get(pk=data["role_id"], tenant=request.user.tenant)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Role not found in your tenant.")
        data["user"] = user
        data["role"] = role
        return data


class UserRoleSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = UserRole
        fields = ("id", "user_name", "user_email", "role_name", "assigned_at")