"""Specimen definitions urls."""

from django.urls import path

from . import views

app_name = "specimendefinitions"

urlpatterns = [
    path(
        "specimendefinitions/",
        views.SpecimenDefinitionListView.as_view(),
    ),
    path(
        "specimendefinitions/<int:pk>/",
        views.SpecimenDefinitionDetailView.as_view(),
    ),
]
