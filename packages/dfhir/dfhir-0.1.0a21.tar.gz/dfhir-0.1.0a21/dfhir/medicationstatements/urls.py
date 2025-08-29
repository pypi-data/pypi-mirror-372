"""medication statement urls."""

from django.urls import path

from dfhir.medicationstatements import views

app_name = "medicationstatements"


urlpatterns = [
    path(
        "medicationstatements/",
        views.MedicationStatementListView.as_view(),
        name="medicationstatement-list",
    ),
    path(
        "medicationstatements/<int:pk>/",
        views.MedicationStatementDetailedView.as_view(),
        name="medicationstatement-detail",
    ),
]
