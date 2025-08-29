"""Claim responses urls."""

from django.urls import path

from . import views

app_name = "claimresponses"


urlpatterns = [
    path("claimresponses/", views.ClaimResponseListView.as_view()),
    path("claimresponses/<int:pk>/", views.ClaimResponseDetailView.as_view()),
]
