"""Devicerequests urls."""

from django.urls import path

from . import views

app_name = "devicerequests"


urlpatterns = [
    path("devicerequests/", views.DeviceRequestListView.as_view()),
    path("devicerequests/<int:pk>/", views.DeviceRequestDetailView.as_view()),
]
