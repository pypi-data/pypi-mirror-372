"""medication url configurations."""

from django.urls import path

from dfhir.medications.views import (
    MedicationCodesList,
    MedicationDetail,
    MedicationDoseFormList,
    MedicationIngredientItemList,
    MedicationsList,
)

app_name = "medications"
urlpatterns = [
    path("medications/", MedicationsList.as_view(), name="medications-list"),
    path(
        "medications/<int:pk>/", MedicationDetail.as_view(), name="medications-detail"
    ),
    path(
        "medication-ingredient-items/",
        MedicationIngredientItemList.as_view(),
        name="medication-ingredient-items-list",
    ),
    path(
        "medication-dose-forms/",
        MedicationDoseFormList.as_view(),
        name="medication-dose-forms-list",
    ),
    path(
        "medication-codes/", MedicationCodesList.as_view(), name="medication-codes-list"
    ),
]
