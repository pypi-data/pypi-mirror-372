"""imaging study URL Configuration."""

from django.urls import path

from dfhir.imagingstudies import views

app_name = "imagingstudies"

urlpatterns = [
    path("imagingstudies/", views.ImagingStudyListView.as_view(), name="list"),
    path(
        "imagingstudies/<int:pk>/",
        views.ImagingStudyDetailView.as_view(),
        name="detail",
    ),
]
