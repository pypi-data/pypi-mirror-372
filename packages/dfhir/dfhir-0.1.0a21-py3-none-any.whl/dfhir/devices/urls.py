"""Device urls."""

from django.urls import path

from . import views

app_name = "devices"

urlpatterns = [
    path("devices/", views.DeviceListView.as_view()),
    path("devices/<int:pk>/", views.DeviceDetailView.as_view()),
]
