"""Patients URL Configuration."""

from django.urls import path

from . import views

app_name = "patients"

urlpatterns = [
    path("patients/", views.PatientListView.as_view()),
    path("patients/<int:pk>/", views.PatientDetailView.as_view()),
]
