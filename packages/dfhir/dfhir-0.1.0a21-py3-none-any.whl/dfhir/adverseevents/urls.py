"""Adverse events urls."""

from django.urls import path

from . import views

app_name = "adverseevents"

urlpatterns = [
    path("adverseevents/", views.AdverseEventListView.as_view(), name="list_view"),
    path(
        "adverseevents/<int:pk>/",
        views.AdverseEventDetailView.as_view(),
        name="detail_view",
    ),
]
