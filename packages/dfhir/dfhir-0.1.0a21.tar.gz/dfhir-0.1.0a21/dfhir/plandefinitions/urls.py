"""Plandefinitions urls."""

from django.urls import path

from . import views

app_name = "plandefinitions"


urlpatterns = [
    path("plandefinitions/", views.PlanDefinitionListView.as_view()),
    path("plandefinitions/<int:pk>/", views.PlanDefinitionDetailView.as_view()),
]
