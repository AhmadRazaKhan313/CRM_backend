from rest_framework import serializers
from .models import Lead, LeadActivity


class LeadActivitySerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)

    class Meta:
        model = LeadActivity
        fields = ("id", "activity_type", "note", "created_by_name", "created_at")


class LeadListSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    contacted_by_name = serializers.CharField(source="contacted_by.full_name", read_only=True)

    class Meta:
        model = Lead
        fields = (
            "id", "full_name", "email", "phone", "country", "company",
            "source", "department", "status", "service_interest",
            "platform_link", "instagram_url", "facebook_url", "linkedin_url",
            "assigned_to_name", "created_by_name", "contacted_by_name",
            "is_archived", "created_at", "updated_at"
        )


class LeadDetailSerializer(serializers.ModelSerializer):
    activities = LeadActivitySerializer(many=True, read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    contacted_by_name = serializers.CharField(source="contacted_by.full_name", read_only=True)

    class Meta:
        model = Lead
        fields = "__all__"


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        exclude = ("tenant", "created_by", "is_archived")

    def create(self, validated_data):
        request = self.context["request"]
        if not validated_data.get("department") and request.user.department:
            validated_data["department"] = request.user.department
        return Lead.objects.create(
            tenant=request.user.tenant,
            created_by=request.user,
            **validated_data
        )