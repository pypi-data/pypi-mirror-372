"""Devicedispenses urls."""

from django.urls import path

from . import views

app_name = "devicedispenses"


urlpatterns = [
    path("devicedispenses/", views.DeviceDispenseListView.as_view()),
    path("devicedispenses/<int:pk>/", views.DeviceDispenseDetailView.as_view()),
]
