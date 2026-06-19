from django.contrib import admin
from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ("name", "tenant", "head", "is_active", "created_at")
    list_filter   = ("is_active", "tenant")
    search_fields = ("name",)
