from django.core.management.base import BaseCommand
from core.models import Permission

PERMISSIONS = [
    # Leads
    ("leads", "view", "View Leads"),
    ("leads", "create", "Create Leads"),
    ("leads", "edit", "Edit Leads"),
    ("leads", "delete", "Delete Leads"),
    ("leads", "assign", "Assign Leads"),
    ("leads", "export", "Export Leads"),
    # Clients
    ("clients", "view", "View Clients"),
    ("clients", "create", "Create Clients"),
    ("clients", "edit", "Edit Clients"),
    ("clients", "delete", "Delete Clients"),
    ("clients", "export", "Export Clients"),
    # Sales
    ("sales", "view", "View Sales"),
    ("sales", "create", "Create Sales"),
    ("sales", "approve", "Approve Sales"),
    ("sales", "export", "Export Sales"),
    # Tasks
    ("tasks", "view", "View Tasks"),
    ("tasks", "create", "Create Tasks"),
    ("tasks", "edit", "Edit Tasks"),
    ("tasks", "delete", "Delete Tasks"),
    ("tasks", "assign", "Assign Tasks"),
    # Reports
    ("reports", "view", "View Reports"),
    ("reports", "create", "Create Reports"),
    ("reports", "export", "Export Reports"),
    # Finance
    ("finance", "view", "View Finance"),
    ("finance", "create", "Create Finance"),
    ("finance", "approve", "Approve Finance"),
    ("finance", "export", "Export Finance"),
    # Employees
    ("employees", "view", "View Employees"),
    ("employees", "create", "Create Employees"),
    ("employees", "edit", "Edit Employees"),
    ("employees", "delete", "Delete Employees"),
    ("employees", "assign", "Assign Roles to Employees"),
    # Departments
    ("departments", "view", "View Departments"),
    ("departments", "create", "Create Departments"),
    ("departments", "edit", "Edit Departments"),
    # Delivery
    ("delivery", "view", "View Deliveries"),
    ("delivery", "edit", "Edit Deliveries"),
    ("delivery", "approve", "Approve Deliveries"),
    # Analytics
    ("analytics", "view", "View Analytics"),
    ("analytics", "export", "Export Analytics"),
    # Settings
    ("settings", "view", "View Settings"),
    ("settings", "edit", "Edit Settings"),
]


class Command(BaseCommand):
    help = "Seed default permissions"

    def handle(self, *args, **kwargs):
        created = 0
        for module, action, label in PERMISSIONS:
            codename = f"{module}.{action}"
            _, made = Permission.objects.get_or_create(
                codename=codename,
                defaults={"module": module, "action": action, "label": label}
            )
            if made:
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"{created} permissions created. {len(PERMISSIONS) - created} already existed."
        ))