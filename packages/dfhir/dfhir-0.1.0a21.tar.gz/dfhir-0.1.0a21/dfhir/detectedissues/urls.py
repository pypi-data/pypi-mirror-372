"""Detected issues urls."""

from django.urls import path

from . import views

app_name = "detectedissues"

urlpatterns = [
    path(
        "detectedissues/",
        views.DetectedIssueListView.as_view(),
        name="detectedissue-list-create",
    ),
    path(
        "detectedissues/<int:pk>/",
        views.DetectedIssueDetailView.as_view(),
        name="detectedissue-detail",
    ),
]
