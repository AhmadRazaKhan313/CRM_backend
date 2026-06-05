from django.urls import path
from . import views

urlpatterns = [
    path("", views.ClientListCreateView.as_view()),
    path("<int:pk>/", views.ClientDetailView.as_view()),
    path("<int:pk>/payments/", views.ClientPaymentView.as_view()),
    path("<int:pk>/files/", views.ClientFileView.as_view()),
]