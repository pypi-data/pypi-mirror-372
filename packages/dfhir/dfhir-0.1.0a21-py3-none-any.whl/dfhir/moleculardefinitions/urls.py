"""molecular definitions URL Configuration."""

from django.urls import path

from dfhir.moleculardefinitions import views

app_name = "moleculardefinitions"


urlpatterns = [
    path("moleculardefinitions/", views.MolecularDefinitionListView.as_view()),
    path(
        "moleculardefinitions/<int:pk>/", views.MolecularDefinitionDetailView.as_view()
    ),
]
