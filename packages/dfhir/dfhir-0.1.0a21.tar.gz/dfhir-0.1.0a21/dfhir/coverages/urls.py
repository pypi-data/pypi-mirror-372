"""Coverage urls."""

from django.urls import path

from . import views

app_name = "coverages"

urlpatterns = [
    path("coverages/", views.CoverageListView.as_view(), name="list_view"),
    path(
        "coverages/<int:pk>/",
        views.CoverageDetailView.as_view(),
        name="detail_view",
    ),
]
