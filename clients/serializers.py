<<<<<<< HEAD
from rest_framework import serializers
from .models import Client, SalesDetail, TechDetail, SEODetail, Payment, ClientFile


class SalesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesDetail
        exclude = ("id", "client")


class TechDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechDetail
        exclude = ("id", "client")


class SEODetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEODetail
        exclude = ("id", "client")


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ("tenant",)
        read_only_fields = ("id", "created_at")


class ClientFileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True)

    class Meta:
        model = ClientFile
        fields = ("id", "name", "file", "uploaded_by_name", "uploaded_at")


class ClientListSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)

    class Meta:
        model = Client
        fields = (
            "id", "full_name", "email", "phone", "country",
            "department", "status", "tag", "assigned_to_name",
            "is_archived", "created_at"
        )


class ClientDetailSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True)
    sales_detail = SalesDetailSerializer(read_only=True)
    tech_detail = TechDetailSerializer(read_only=True)
    seo_detail = SEODetailSerializer(read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    files = ClientFileSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = "__all__"


class ClientCreateSerializer(serializers.ModelSerializer):
    sales_detail = SalesDetailSerializer(required=False)
    tech_detail = TechDetailSerializer(required=False)
    seo_detail = SEODetailSerializer(required=False)

    class Meta:
        model = Client
        exclude = ("tenant", "created_by", "is_archived")

    def create(self, validated_data):
        sales = validated_data.pop("sales_detail", None)
        tech = validated_data.pop("tech_detail", None)
        seo = validated_data.pop("seo_detail", None)
        request = self.context["request"]

        client = Client.objects.create(
            tenant=request.user.tenant,
            created_by=request.user,
            **validated_data
        )
        if sales:
            SalesDetail.objects.create(client=client, **sales)
        if tech:
            TechDetail.objects.create(client=client, **tech)
        if seo:
            SEODetail.objects.create(client=client, **seo)
        return client
=======
from rest_framework import serializers
from .models import Client, SalesDetail, TechDetail, SEODetail, Payment, ClientFile


class SalesDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesDetail
        exclude = ("client",)


class TechDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechDetail
        exclude = ("client",)


class SEODetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEODetail
        exclude = ("client",)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ("tenant", "client")
        read_only_fields = ("paid_at", "created_at")


class ClientFileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source="uploaded_by.full_name", read_only=True)

    class Meta:
        model = ClientFile
        fields = ("id", "file", "name", "uploaded_by_name", "uploaded_at")
        read_only_fields = ("uploaded_at",)


class ClientListSerializer(serializers.ModelSerializer):
    assigned_to_name  = serializers.CharField(source="assigned_to.full_name",  read_only=True)
    created_by_name   = serializers.CharField(source="created_by.full_name",   read_only=True)
    converted_from_id = serializers.IntegerField(source="converted_from.id",   read_only=True)

    class Meta:
        model  = Client
        fields = (
            "id", "full_name", "email", "phone", "country", "company",
            "department", "status", "tag",
            "assigned_to", "assigned_to_name",
            "converted_from_id",
            "created_by_name",
            "is_archived", "created_at", "updated_at",
        )


class ClientDetailSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source="assigned_to.full_name", read_only=True)
    created_by_name  = serializers.CharField(source="created_by.full_name",  read_only=True)

    # Department-specific details — null agar exist nahi karta
    sales_detail = SalesDetailSerializer(read_only=True)
    tech_detail  = TechDetailSerializer(read_only=True)
    seo_detail   = SEODetailSerializer(read_only=True)

    # Related data
    payments = PaymentSerializer(many=True, read_only=True)
    files    = ClientFileSerializer(many=True, read_only=True)

    # Converted from lead
    converted_from_name = serializers.SerializerMethodField()

    class Meta:
        model  = Client
        fields = (
            "id", "full_name", "email", "phone", "country", "company",
            "department", "status", "tag",
            "assigned_to", "assigned_to_name",
            "converted_from", "converted_from_name",
            "created_by_name",
            "notes",
            "sales_detail", "tech_detail", "seo_detail",
            "payments", "files",
            "is_archived", "created_at", "updated_at",
        )

    def get_converted_from_name(self, obj):
        if obj.converted_from:
            return obj.converted_from.full_name
        return None


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Client
        exclude = ("tenant", "created_by", "is_archived", "converted_from")

    def create(self, validated_data):
        request = self.context["request"]
        if not validated_data.get("department") and request.user.department:
            validated_data["department"] = request.user.department
        return Client.objects.create(
            tenant     = request.user.tenant,
            created_by = request.user,
            **validated_data
        )
>>>>>>> main
