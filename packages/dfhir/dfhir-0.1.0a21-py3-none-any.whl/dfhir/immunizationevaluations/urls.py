"""immunization evaluations URL Configuration."""

from django.urls import path

from dfhir.immunizationevaluations import views

app_name = "immunizationevaluations"

urlpatterns = [
    path("immunizationevaluations/", views.ImmunizationEvaluationListView.as_view()),
    path(
        "immunizationevaluations/<int:pk>",
        views.ImmunizationEvaluationDetailView.as_view(),
    ),
]
