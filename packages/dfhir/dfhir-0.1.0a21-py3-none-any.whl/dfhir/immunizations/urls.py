"""immunization app urls."""

from django.urls import path

from dfhir.immunizations import views

app_name = "immunizations"
urlpatterns = [
    path(
        "immunizations/",
        views.ImmunizationListView.as_view(),
        name="immunization-list-create",
    ),
    path(
        "immunizations/<int:pk>/",
        views.ImmunizationDetailView.as_view(),
        name="immunization-retrieve-update-destroy",
    ),
]
