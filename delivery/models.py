from django.db import models
from tenants.mixins import TenantModel


class Delivery(TenantModel):
    """
    Client project delivery tracking.
    Ek client ke liye ek ya zyada deliveries ho sakti hain.
    """
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW      = "review",      "In Review"
        DELIVERED   = "delivered",   "Delivered"
        ACCEPTED    = "accepted",    "Accepted"
        REVISION    = "revision",    "Needs Revision"

    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="deliveries"
    )
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department  = models.CharField(max_length=20, blank=True)

    status      = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_STARTED)
    progress    = models.PositiveIntegerField(default=0)  # 0-100

    assigned_to = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="assigned_deliveries"
    )
    created_by  = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_deliveries"
    )

    start_date   = models.DateField(null=True, blank=True)
    due_date     = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    delivery_link = models.URLField(blank=True)   # Google Drive / file link
    notes         = models.TextField(blank=True)

    is_archived = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "deliveries"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} — {self.client.full_name}"


class Milestone(models.Model):
    """Delivery ke andar chhote milestones."""
    delivery   = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name="milestones")
    title      = models.CharField(max_length=200)
    is_done    = models.BooleanField(default=False)
    due_date   = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "delivery_milestones"
        ordering = ["created_at"]

    def __str__(self):
        return self.title
