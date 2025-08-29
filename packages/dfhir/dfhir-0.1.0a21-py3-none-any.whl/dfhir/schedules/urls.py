"""Schedule URL Configuration."""

from django.urls import path

from . import views

app_name = "schedules"

urlpatterns = [
    path("schedules/", views.ScheduleListView.as_view(), name="schedule-list"),
    path(
        "schedules/<int:pk>/",
        views.ScheduleDetailView.as_view(),
        name="schedule-detail",
    ),
]
