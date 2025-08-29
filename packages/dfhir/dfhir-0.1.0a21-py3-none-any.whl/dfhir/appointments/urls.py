"""Appointments URL Configuration."""

from django.urls import path

from .views import AppointmentDetailView, AppointmentListView

app_name = "appointments"

urlpatterns = [
    path("appointments/", AppointmentListView.as_view(), name="appointment-list"),
    path(
        "appointments/<int:pk>/",
        AppointmentDetailView.as_view(),
        name="appointment-detail",
    ),
]
