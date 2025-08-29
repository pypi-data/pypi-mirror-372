"""Clinical impressions urls."""

from django.urls import path

from . import views

app_name = "clinicalimpressions"

urlpatterns = [
    path(
        "clincalimpressions/", views.ClinicalImpressionListView.as_view(), name="create"
    ),
    path(
        "clincalimpressions/<int:pk>/",
        views.ClinicalImpressionsDetailView.as_view(),
        name="detail",
    ),
]
