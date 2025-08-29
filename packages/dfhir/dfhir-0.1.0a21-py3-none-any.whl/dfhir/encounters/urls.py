"""Encounter urls."""

from django.urls import path

from . import views

app_name = "encounters"

urlpatterns = [
    path("encounters/", views.EncounterListView.as_view()),
    path("encounters/<int:pk>/", views.EncounterDetailView.as_view()),
    path("encounters/conditions/", views.EncounterConditionListView.as_view()),
    path("encounters/diet/", views.DietPreferenceListView.as_view()),
    path("encounters/courtesy/", views.SpecialArrangementListView.as_view()),
    path("encounters/arrangement/", views.SpecialArrangementListView.as_view()),
]
