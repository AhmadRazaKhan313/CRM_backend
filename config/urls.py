from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("authentication.urls")),
    path("api/tenant/", include("tenants.urls")),
    path("api/core/", include("core.urls")),
    path("api/leads/", include("leads.urls")),
    path("api/tasks/", include("tasks.urls")),
    path("api/reports/", include("reports.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)