from django.urls import path
from . import views

urlpatterns = [
    path("",                       views.DeliveryListCreateView.as_view()),
    path("<int:pk>/",              views.DeliveryDetailView.as_view()),
    path("<int:pk>/milestones/",   views.MilestoneView.as_view()),
    path("milestones/<int:pk>/",   views.MilestoneView.as_view()),
]
