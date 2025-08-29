"""Appointment responses urls."""

from django.urls import path

from . import views

app_name = "appointmentresponses"

urlpatterns = [
    path(
        "appointmentresponses/",
        views.AppointmentResponseListView.as_view(),
        name="list-create",
    ),
    path(
        "appointmentresponses/<int:pk>/",
        views.AppointmentResponseDetailView.as_view(),
        name="detail",
    ),
]
