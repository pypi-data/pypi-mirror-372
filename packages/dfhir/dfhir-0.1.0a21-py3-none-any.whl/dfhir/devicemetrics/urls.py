"""Device metrics url."""

from django.urls import path

from . import views

app_name = "devicemetrics"

urlpatterns = [
    path("devicemetrics/", views.DeviceMetricListView.as_view()),
    path("devicemetrics/<int:pk>/", views.DeviceMetricDetailView.as_view()),
]
