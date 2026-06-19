from rest_framework import serializers
from .models import Delivery, Milestone


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Milestone
        fields = ("id", "title", "is_done", "due_date", "created_at")
        read_only_fields = ("id", "created_at")


class DeliveryListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)
    client_name      = serializers.CharField(source="client.full_name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)
    milestone_count  = serializers.SerializerMethodField()
    done_count       = serializers.SerializerMethodField()

    class Meta:
        model  = Delivery
        fields = (
            "id", "title", "client", "client_name",
            "department", "department_name", "status", "progress",
            "assigned_to", "assigned_to_name",
            "start_date", "due_date", "delivered_at",
            "milestone_count", "done_count",
            "created_at",
        )

    def get_milestone_count(self, obj):
        return obj.milestones.count()

    def get_done_count(self, obj):
        return obj.milestones.filter(is_done=True).count()


class DeliveryDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)
    client_name      = serializers.CharField(source="client.full_name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)
    created_by_name  = serializers.CharField(source="created_by.full_name", read_only=True)
    milestones       = MilestoneSerializer(many=True, read_only=True)

    class Meta:
        model  = Delivery
        fields = (
            "id", "title", "description", "client", "client_name",
            "department", "department_name", "status", "progress",
            "assigned_to", "assigned_to_name",
            "created_by_name",
            "start_date", "due_date", "delivered_at",
            "delivery_link", "notes",
            "milestones",
            "created_at", "updated_at",
        )


class DeliveryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model   = Delivery
        exclude = ("tenant", "created_by", "is_archived", "delivered_at")

    def create(self, validated_data):
        request = self.context["request"]
        return Delivery.objects.create(
            tenant     = request.user.tenant,
            created_by = request.user,
            **validated_data
        )
