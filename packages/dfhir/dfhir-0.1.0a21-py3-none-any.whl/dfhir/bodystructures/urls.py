"""body structure urls."""

from django.urls import path

from dfhir.bodystructures.views import BodyStructureDetailView, BodyStructureListView

app_name = "bodystructures"

urlpatterns = [
    path("bodystructures/", BodyStructureListView.as_view(), name="bodystructure-list"),
    path(
        "bodystructures/<int:pk>/",
        BodyStructureDetailView.as_view(),
        name="bodystructure-detail",
    ),
]
