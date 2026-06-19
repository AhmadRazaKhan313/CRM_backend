from django.db import models
from tenants.mixins import TenantModel


class Department(TenantModel):
    """
    Custom department — har organization apne departments banati hai.
    Koi hardcoded type nahi (pehle sales/tech/seo hardcoded the).
    """
    name        = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="headed_department",
    )
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "departments"
        ordering = ["name"]
        unique_together = ("tenant", "name")

    def __str__(self):
        return self.name
