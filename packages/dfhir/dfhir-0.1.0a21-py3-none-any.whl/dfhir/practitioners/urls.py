"""Practitioners URL Configuration."""

from django.urls import path

from . import views

app_name = "practitioners"

urlpatterns = [
    path("practitioners/", views.PractitionerListView.as_view()),
    path("practitioners/<int:pk>/", views.PractitionerDetailView.as_view()),
]
