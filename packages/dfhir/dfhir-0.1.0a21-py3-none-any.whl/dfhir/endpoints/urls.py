"""Endpoints urls."""

from django.urls import path

from . import views

app_name = "endpoints"

urlpatterns = [
    path("endpoints/", views.EndpointListView.as_view()),
    path("endpoints/<int:pk>/", views.EndpointDetailView.as_view()),
]
