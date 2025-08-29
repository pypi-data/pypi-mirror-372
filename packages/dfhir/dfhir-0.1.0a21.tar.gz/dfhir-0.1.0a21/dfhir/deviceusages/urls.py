"""Device usages urls."""

from django.urls import path

from . import views

app_name = "deviceusages"


urlpatterns = [
    path("deviceusages/", views.DeviceUsageListView.as_view()),
    path("deviceusages/<int:pk>/", views.DeviceUsageDetailView.as_view()),
]
