"""observation definitions urls."""

from django.urls import path

from dfhir.observationdefinitions.views import (
    ObservationDefinitionDetailView,
    ObservationDefinitionListView,
)

app_name = "observationdefinitions"

urlpatterns = [
    path(
        "observationdefinitions/",
        ObservationDefinitionListView.as_view(),
        name="observationdefinitions",
    ),
    path(
        "observationdefinitions/<int:pk>/",
        ObservationDefinitionDetailView.as_view(),
        name="observationdefinition",
    ),
]
