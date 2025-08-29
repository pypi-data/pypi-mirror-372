"""observations urls."""

from django.urls import path

from . import views

app_name = "observations"

urlpatterns = [
    path("observations/", views.ObservationListView.as_view(), name="list_view"),
    path(
        "observations/<int:pk>/",
        views.ObservationDetailView.as_view(),
        name="detail_view",
    ),
]
