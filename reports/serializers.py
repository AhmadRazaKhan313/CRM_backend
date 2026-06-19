from rest_framework import serializers
from .models import DailyReport


class DailyReportListSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True, default=None)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True)

    class Meta:
        model = DailyReport
        fields = (
            "id", "employee_name", "date",
            "department", "department_name", "status", "total_leads", "total_calls",
            "total_conversions", "reviewed_by_name", "created_at"
        )


class DailyReportDetailSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source="employee.full_name", read_only=True)
    reviewed_by_name = serializers.CharField(source="reviewed_by.full_name", read_only=True)

    class Meta:
        model = DailyReport
        fields = "__all__"


class DailyReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyReport
        exclude = ("tenant", "employee", "reviewed_by", "status", "manager_feedback")

    def validate(self, data):
        request = self.context["request"]
        date = data.get("date")
        if DailyReport.objects.filter(employee=request.user, date=date).exists():
            raise serializers.ValidationError("You already submitted a report for this date.")
        return data

    def create(self, validated_data):
        request = self.context["request"]
        return DailyReport.objects.create(
            tenant=request.user.tenant,
            employee=request.user,
            **validated_data
        )


class ReportReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["reviewed", "flagged"])
    manager_feedback = serializers.CharField(required=False, allow_blank=True)