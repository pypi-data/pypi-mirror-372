"""document reference urls."""

from django.urls import path

from dfhir.documentreferences.views import (
    DocumentReferenceDetailView,
    DocumentReferenceListView,
)

app_name = "documentreferences"

urlpatterns = [
    path(
        "documentreferences/",
        DocumentReferenceListView.as_view(),
        name="documentreference-list",
    ),
    path(
        "documentreferences/<int:pk>/",
        DocumentReferenceDetailView.as_view(),
        name="documentreference-detail",
    ),
]
