"""medication dispenses urls."""

from django.urls import path

from dfhir.medicationdispenses.views import (
    MedicationDispenseDetailView,
    MedicationDispenseListView,
)

app_name = "medicationdispenses"

urlpatterns = [
    path(
        "medicationdispenses/",
        MedicationDispenseListView.as_view(),
        name="medicationdispense-list",
    ),
    path(
        "medicationdispenses/<int:pk>/",
        MedicationDispenseDetailView.as_view(),
        name="medicationdispense-detail",
    ),
]
