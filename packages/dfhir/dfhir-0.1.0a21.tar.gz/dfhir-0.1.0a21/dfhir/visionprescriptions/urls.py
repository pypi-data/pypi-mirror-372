"""Vision prescription urls."""

from django.urls import path

from . import views

app_name = "visionprescriptions"


urlpatterns = [
    path(
        "visionprescriptions/",
        views.VisionPrescriptionListView.as_view(),
        name="visionprescriptions-list",
    ),
    path(
        "visionprescriptions/<int:pk>/",
        views.VisionPrescriptionDetailView.as_view(),
        name="visionprescription-details",
    ),
]
