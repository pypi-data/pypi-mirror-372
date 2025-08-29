"""CoverageEligibilityResponse urls."""

from django.urls import path

from . import views

app_name = "coverageeligibilityresponses"

urlpatterns = [
    path(
        "coverageeligibilityresponses/",
        views.CoverageEligibilityResponseListView.as_view(),
        name="list-create",
    ),
    path(
        "coverageeligibilityresponses/<int:pk>/",
        views.CoverageEligibilityResponseDetailView.as_view(),
        name="detail",
    ),
]
