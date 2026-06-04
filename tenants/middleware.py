from django.http import JsonResponse
from .models import Tenant


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(":")[0]  # localhost:8000 → localhost
        parts = host.split(".")

        # subdomain.domain.com → subdomain is tenant slug
        # localhost pe development mein header se lenge
        slug = request.headers.get("X-Tenant-Slug") or (
            parts[0] if len(parts) > 2 else None
        )

        if slug and slug not in ("www", "api", "admin"):
            try:
                tenant = Tenant.objects.select_related("features").get(
                    slug=slug, status__in=("active", "trial")
                )
                request.tenant = tenant
            except Tenant.DoesNotExist:
                return JsonResponse({"detail": "Invalid tenant."}, status=404)
        else:
            request.tenant = None

        return self.get_response(request)