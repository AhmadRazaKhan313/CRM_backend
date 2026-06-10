from django.db import models
from tenants.mixins import TenantModel


class Lead(TenantModel):
    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        INTERESTED = "interested", "Interested"
        FOLLOW_UP = "follow_up", "Follow Up"
        CONVERTED = "converted", "Converted"
        REJECTED = "rejected", "Rejected"

    class Source(models.TextChoices):
        INSTAGRAM = "instagram", "Instagram"
        FACEBOOK = "facebook", "Facebook"
        LINKEDIN = "linkedin", "LinkedIn"
        WHATSAPP = "whatsapp", "WhatsApp"
        WEBSITE = "website", "Website"
        EMAIL = "email", "Email"
        OTHER = "other", "Other"

    class Department(models.TextChoices):
        SALES = "sales", "Sales"
        TECH = "tech", "Tech"
        SEO = "seo", "SEO"

    # Basic Info
    full_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=60, blank=True)
    company = models.CharField(max_length=120, blank=True)

    # Lead Details
    source = models.CharField(max_length=20, choices=Source.choices)
    department = models.CharField(max_length=20, choices=Department.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    service_interest = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)
    questionnaire = models.TextField(blank=True)
    platform_link = models.URLField(blank=True)

    # Assignment
    assigned_to = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assigned_leads"
    )
    created_by = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_leads"
    )
    contacted_by = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="contacted_leads"
    )

    # Social
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "leads"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.status}"


class LeadActivity(models.Model):
    class ActivityType(models.TextChoices):
        NOTE = "note", "Note"
        CALL = "call", "Call"
        EMAIL = "email", "Email"
        WHATSAPP = "whatsapp", "WhatsApp"
        MEETING = "meeting", "Meeting"
        STATUS_CHANGE = "status_change", "Status Change"

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=20, choices=ActivityType.choices)
    note = models.TextField()
    created_by = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lead_activities"
        ordering = ["-created_at"]