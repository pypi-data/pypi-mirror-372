"""Substances urls."""

from django.urls import path

from . import views

app_name = "substances"

urlpatterns = [
    path("substances/", views.SubstanceListView.as_view()),
    path("substances/<int:pk>/", views.SubstanceDetailView.as_view()),
]
