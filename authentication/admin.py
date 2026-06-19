from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ("email", "full_name", "tenant", "employee_id", "is_super_admin", "is_active")
    list_filter   = ("is_super_admin", "is_active", "tenant")
    search_fields = ("email", "full_name", "employee_id")
    ordering      = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("full_name", "phone", "avatar")}),
        ("Organization", {"fields": ("tenant", "employee_id")}),
        ("Permissions", {"fields": ("is_super_admin", "is_active", "is_staff", "is_superuser")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "tenant", "password1", "password2"),
        }),
    )
