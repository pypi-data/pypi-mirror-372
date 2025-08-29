"""CoverageEligibilityRequests URL Configuration."""

from django.urls import path

from . import views

app_name = "coverageeligibilityrequests"


urlpatterns = [
    path(
        "coverageeligibilityrequests/",
        views.CoverageEligibilityRequestListView.as_view(),
        name="list-create",
    ),
    path(
        "coverageeligibilityrequests/<int:pk>/",
        views.CoverageEligibilityRequestDetailView.as_view(),
        name="detail",
    ),
]
