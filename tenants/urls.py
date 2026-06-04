from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.TenantRegisterView.as_view()),
    path("me/", views.TenantDetailView.as_view()),
]