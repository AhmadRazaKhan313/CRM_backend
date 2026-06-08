from django.contrib import admin
from .models import Client, SalesDetail, TechDetail, SEODetail, Payment, ClientFile


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("full_name", "department", "status", "tag", "assigned_to", "created_at")
    list_filter = ("status", "department", "tag")
    search_fields = ("full_name", "email", "phone")


@admin.register(SalesDetail)
class SalesDetailAdmin(admin.ModelAdmin):
    list_display = ("client", "platform")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("client", "amount", "paid_amount", "status", "method", "created_at")
    list_filter = ("status", "method")