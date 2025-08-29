"""Allergy intolerances URLs."""

from django.urls import path

from . import views

app_name = "allergyintolerances"


urlpatterns = [
    path(
        "allergyintolerances/",
        views.AllergyIntoleranceListView.as_view(),
        name="allergyintolerance-list-create",
    ),
    path(
        "allergyintolerances/<int:pk>/",
        views.AllergyIntoleranceDetailView.as_view(),
        name="allergyintolerance-retrieve-update-destroy",
    ),
]
