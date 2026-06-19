from django.core.management.base import BaseCommand
from core.models import Permission

# (module, action, codename, label)
PERMISSIONS = [
    # Leads
    ("leads", "view",     "leads.view",     "View Leads"),
    ("leads", "view_all", "leads.view_all", "View All Leads (not just assigned)"),
    ("leads", "create",   "leads.create",   "Create Leads"),
    ("leads", "edit",     "leads.edit",     "Edit Leads"),
    ("leads", "delete",   "leads.delete",   "Delete Leads"),
    ("leads", "export",   "leads.export",   "Export Leads"),
    ("leads", "assign",   "leads.assign",   "Assign Leads"),
    # Clients
    ("clients", "view",     "clients.view",     "View Clients"),
    ("clients", "view_all", "clients.view_all", "View All Clients"),
    ("clients", "create",   "clients.create",   "Create Clients"),
    ("clients", "edit",     "clients.edit",     "Edit Clients"),
    ("clients", "delete",   "clients.delete",   "Delete Clients"),
    ("clients", "export",   "clients.export",   "Export Clients"),
    ("clients", "assign",   "clients.assign",   "Assign Clients"),
    # Tasks
    ("tasks", "view",     "tasks.view",     "View Tasks"),
    ("tasks", "view_all", "tasks.view_all", "View All Tasks"),
    ("tasks", "create",   "tasks.create",   "Create Tasks"),
    ("tasks", "edit",     "tasks.edit",     "Edit Tasks"),
    ("tasks", "delete",   "tasks.delete",   "Delete Tasks"),
    ("tasks", "assign",   "tasks.assign",   "Assign Tasks"),
    # Reports
    ("reports", "view",     "reports.view",     "View Reports"),
    ("reports", "view_all", "reports.view_all", "View All Reports"),
    ("reports", "create",   "reports.create",   "Submit Reports"),
    ("reports", "approve",  "reports.approve",  "Review/Approve Reports"),
    # Finance
    ("finance", "view",   "finance.view",   "View Finance"),
    ("finance", "create", "finance.create", "Create Invoices/Expenses"),
    ("finance", "edit",   "finance.edit",   "Edit Invoices/Expenses"),
    ("finance", "delete", "finance.delete", "Delete Invoices/Expenses"),
    ("finance", "export", "finance.export", "Export Finance"),
    # Employees
    ("employees", "view",   "employees.view",   "View Employees"),
    ("employees", "create", "employees.create", "Add Employees"),
    ("employees", "edit",   "employees.edit",   "Edit Employees"),
    ("employees", "delete", "employees.delete", "Deactivate Employees"),
    # Departments
    ("departments", "view",   "departments.view",   "View Departments"),
    ("departments", "create", "departments.create", "Create Departments"),
    ("departments", "edit",   "departments.edit",   "Edit Departments"),
    ("departments", "delete", "departments.delete", "Deactivate Departments"),
    # Delivery
    ("delivery", "view",     "delivery.view",     "View Deliveries"),
    ("delivery", "view_all", "delivery.view_all", "View All Deliveries"),
    ("delivery", "create",   "delivery.create",   "Create Deliveries"),
    ("delivery", "edit",     "delivery.edit",     "Edit Deliveries"),
    ("delivery", "delete",   "delivery.delete",   "Delete Deliveries"),
    # Analytics
    ("analytics", "view", "analytics.view", "View Analytics"),
    # HRMS
    ("hrms", "view",    "hrms.view",    "View HRMS"),
    ("hrms", "create",  "hrms.create",  "Manage Attendance/Shifts"),
    ("hrms", "approve", "hrms.approve", "Approve Leaves"),
    ("hrms", "edit",    "hrms.edit",    "Manage Salary/Payroll"),
    # Roles
    ("roles", "view",   "roles.view",   "View Roles"),
    ("roles", "create", "roles.create", "Create Roles"),
    ("roles", "edit",   "roles.edit",   "Edit Roles"),
    ("roles", "delete", "roles.delete", "Delete Roles"),
    # Notifications
    ("notifications", "view", "notifications.view", "View Notifications"),
    # Settings
    ("settings", "view", "settings.view", "View Settings"),
    ("settings", "edit", "settings.edit", "Edit Settings"),
]


class Command(BaseCommand):
    help = "Seed all permissions into the database"

    def handle(self, *args, **kwargs):
        created = 0
        skipped = 0
        for module, action, codename, label in PERMISSIONS:
            _, was_created = Permission.objects.get_or_create(
                codename=codename,
                defaults={"module": module, "action": action, "label": label},
            )
            if was_created:
                created += 1
            else:
                skipped += 1
        self.stdout.write(self.style.SUCCESS(
            f"Done — {created} created, {skipped} already existed. Total: {len(PERMISSIONS)}"
        ))
