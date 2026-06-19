from django.core.management.base import BaseCommand
from django.db import transaction
from tenants.models import Tenant, TenantFeature
from authentication.models import User


class Command(BaseCommand):
    help = "Create the primary Organization (Org 1) and its Super Admin (website owner)."

    def add_arguments(self, parser):
        parser.add_argument("--email",    default="admin@crm.com")
        parser.add_argument("--password", default="Admin@1234")
        parser.add_argument("--name",     default="Owner")
        parser.add_argument("--org-name", default="Organization 1")

    @transaction.atomic
    def handle(self, *args, **opts):
        email    = opts["email"].lower().strip()
        password = opts["password"]
        name     = opts["name"]
        org_name = opts["org_name"]

        # Primary organization already hai?
        primary = Tenant.objects.filter(is_primary=True).first()
        if primary:
            self.stdout.write(self.style.WARNING(
                f"Primary organization already exists: {primary.name} (id={primary.id})"
            ))
            org = primary
        else:
            org = Tenant.objects.create(
                name=org_name,
                slug="organization-1",
                email=email,
                plan=Tenant.Plan.ENTERPRISE,
                status=Tenant.Status.ACTIVE,
                is_primary=True,
            )
            TenantFeature.objects.create(
                tenant=org,
                hrms=True, analytics=True, finance_module=True,
                delivery_module=True, ai_assistant=True,
                custom_branding=True, api_access=True,
            )
            self.stdout.write(self.style.SUCCESS(
                f"Created primary organization: {org.name} (id={org.id})"
            ))

        # Super Admin user
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f"User {email} already exists. Skipping."))
        else:
            user = User.objects.create_user(
                email=email,
                password=password,
                full_name=name,
                tenant=org,
                is_super_admin=True,
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS(
                f"Created Super Admin: {user.email} (id={user.id}) in {org.name}"
            ))

        self.stdout.write(self.style.SUCCESS("\nSeeding complete."))
        self.stdout.write(f"  Login email:    {email}")
        self.stdout.write(f"  Login password: {password}")
