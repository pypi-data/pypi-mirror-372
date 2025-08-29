"""immunization recommendation urls."""

from django.urls import path

from dfhir.immunizationrecommendations.views import (
    ImmunizationRecommendationDetailView,
    ImmunizationRecommendationListView,
)

app_name = "immunizationrecommendations"

urlpatterns = [
    path(
        "immunizationrecommendations/",
        ImmunizationRecommendationListView.as_view(),
        name="immunizationrecommendation-list",
    ),
    path(
        "immunizationrecommendations/<int:pk>/",
        ImmunizationRecommendationDetailView.as_view(),
        name="immunizationrecommendation-detail",
    ),
]
