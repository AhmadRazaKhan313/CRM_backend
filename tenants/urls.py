from django.urls import path
from . import views

urlpatterns = [
    # Authenticated — apni organization
    path("me/", views.TenantDetailView.as_view()),

    # Sirf primary super admin nayi organization bana sakta hai
    path("organizations/", views.OrganizationCreateView.as_view()),

    # Super Admin — organization management
    path("admin/stats/",                              views.SuperAdminStatsView.as_view()),
    path("admin/tenants/",                            views.SuperAdminTenantListView.as_view()),
    path("admin/tenants/<int:tenant_id>/",            views.SuperAdminTenantDetailView.as_view()),
    path("admin/tenants/<int:tenant_id>/features/",   views.SuperAdminFeatureFlagView.as_view()),
]
