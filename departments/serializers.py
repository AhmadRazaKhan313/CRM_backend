from rest_framework import serializers
from .models import Department
from authentication.models import User


class DepartmentSerializer(serializers.ModelSerializer):
    head_name  = serializers.CharField(source="head.full_name", read_only=True)
    head_email = serializers.CharField(source="head.email",     read_only=True)

    employee_count = serializers.SerializerMethodField()
    lead_count     = serializers.SerializerMethodField()
    client_count   = serializers.SerializerMethodField()
    active_tasks   = serializers.SerializerMethodField()

    class Meta:
        model  = Department
        fields = (
            "id", "name", "description",
            "head", "head_name", "head_email",
            "is_active", "created_at",
            "employee_count", "lead_count",
            "client_count", "active_tasks",
        )
        read_only_fields = ("id", "created_at")

    def get_employee_count(self, obj):
        # Department ka head + future: members. Abhi head-based.
        return User.objects.filter(
            tenant=obj.tenant, headed_department=obj, is_active=True
        ).count()

    def get_lead_count(self, obj):
        return obj.leads.filter(is_archived=False).count()

    def get_client_count(self, obj):
        return obj.clients.filter(is_archived=False).count()

    def get_active_tasks(self, obj):
        return obj.tasks.filter(
            is_archived=False,
            status__in=("pending", "in_progress"),
        ).count()
