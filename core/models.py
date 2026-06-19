from django.db import models


class Permission(models.Model):
    """
    System ke saare possible actions. Yeh seed data hai —
    seed_permissions command se create hote hain.
    Custom roles inhi permissions mein se choose karte hain.
    """
    class Module(models.TextChoices):
        LEADS         = "leads",         "Leads"
        CLIENTS       = "clients",       "Clients"
        TASKS         = "tasks",         "Tasks"
        REPORTS       = "reports",       "Reports"
        FINANCE       = "finance",       "Finance"
        EMPLOYEES     = "employees",     "Employees"
        DEPARTMENTS   = "departments",   "Departments"
        DELIVERY      = "delivery",      "Delivery"
        ANALYTICS     = "analytics",     "Analytics"
        HRMS          = "hrms",          "HRMS"
        ROLES         = "roles",         "Roles"
        NOTIFICATIONS = "notifications", "Notifications"
        SETTINGS      = "settings",      "Settings"

    class Action(models.TextChoices):
        VIEW     = "view",     "View"
        VIEW_ALL = "view_all", "View All"
        CREATE   = "create",   "Create"
        EDIT     = "edit",     "Edit"
        DELETE   = "delete",   "Delete"
        EXPORT   = "export",   "Export"
        APPROVE  = "approve",  "Approve"
        ASSIGN   = "assign",   "Assign"

    module   = models.CharField(max_length=30, choices=Module.choices)
    action   = models.CharField(max_length=20, choices=Action.choices)
    codename = models.CharField(max_length=60, unique=True)
    label    = models.CharField(max_length=100)

    class Meta:
        db_table = "permissions"
        ordering = ["module", "action"]

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.codename:
            self.codename = f"{self.module}.{self.action}"
        super().save(*args, **kwargs)


class Role(models.Model):
    """
    Custom role — har organization apne roles banati hai.
    Koi system role nahi (super admin ek alag flag hai User pe).
    Role ki permissions hi decide karti hain ke user kya kar sakta hai
    aur uska dashboard kaisa hoga.
    """
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="roles",
    )
    name        = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(Permission, blank=True, related_name="roles")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "roles"
        unique_together = ("tenant", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"


class UserRole(models.Model):
    """User ko custom role assign karna."""
    user = models.ForeignKey(
        "authentication.User",
        on_delete=models.CASCADE,
        related_name="assigned_roles",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="assigned_users",
    )
    assigned_by = models.ForeignKey(
        "authentication.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="roles_assigned",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_roles"
        unique_together = ("user", "role")

    def __str__(self):
        return f"{self.user} -> {self.role}"
