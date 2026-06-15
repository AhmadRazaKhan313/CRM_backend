"""
Seed default Leave Types
Run: python manage.py shell < seed_leave_types.py
"""
from hrms.models import LeaveType
from tenants.models import Tenant

leave_types = [
    {"name": "Annual Leave",    "max_days_per_year": 15, "description": "Yearly paid leave"},
    {"name": "Sick Leave",      "max_days_per_year": 10, "description": "Medical/sick leave"},
    {"name": "Casual Leave",    "max_days_per_year": 7,  "description": "Short notice leave"},
    {"name": "Maternity Leave", "max_days_per_year": 90, "description": "Maternity leave"},
    {"name": "Emergency Leave", "max_days_per_year": 3,  "description": "Family emergency"},
    {"name": "Unpaid Leave",    "max_days_per_year": 30, "description": "Leave without pay"},
]

tenants = Tenant.objects.all()
created_total = 0

for tenant in tenants:
    for lt in leave_types:
        obj, created = LeaveType.objects.get_or_create(
            tenant=tenant,
            name=lt["name"],
            defaults={
                "max_days_per_year": lt["max_days_per_year"],
                "description": lt["description"],
                "is_active": True,
            }
        )
        if created:
            created_total += 1
            print(f"  [{tenant.name}] Created: {lt['name']}")
        else:
            print(f"  [{tenant.name}] Exists:  {lt['name']}")

print(f"\nDone — {created_total} leave types created.")
