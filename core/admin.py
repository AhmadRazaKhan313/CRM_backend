from django.contrib import admin
from .models import Permission, Role, UserRole


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display  = ("label", "module", "action", "codename")
    list_filter   = ("module", "action")
    search_fields = ("label", "codename")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display      = ("name", "tenant", "created_at")
    list_filter       = ("tenant",)
    search_fields     = ("name",)
    filter_horizontal = ("permissions",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_by", "assigned_at")
