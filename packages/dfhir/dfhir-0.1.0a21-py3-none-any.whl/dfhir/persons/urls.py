"""Persons URL Configuration."""

from django.urls import path

from . import views

app_name = "persons"

urlpatterns = [
    path("persons/", views.PersonListView.as_view()),
    path("persons/<int:pk>/", views.PersonDetailView.as_view()),
]
