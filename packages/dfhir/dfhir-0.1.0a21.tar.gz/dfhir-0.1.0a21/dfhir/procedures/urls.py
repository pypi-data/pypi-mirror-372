"""Procedures urls."""

from django.urls import path

from . import views

app_name = "procedures"


urlpatterns = [
    path(
        "procedures/", views.ProcedureListView.as_view(), name="procedure-list-create"
    ),
    path(
        "procedures/<int:pk>/",
        views.ProcedureDetailView.as_view(),
        name="procedure-retrieve-update-destroy",
    ),
]
