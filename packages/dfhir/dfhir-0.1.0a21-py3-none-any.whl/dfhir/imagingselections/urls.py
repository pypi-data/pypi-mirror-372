"""imaging selection url config."""

from django.urls import path

from dfhir.imagingselections import views

app_name = "imagingselections"

urlpatterns = [
    path("imagingselections/", views.ImagingSelectionListView.as_view()),
    path("imagingselections/<int:pk>/", views.ImagingSelectionDetailView.as_view()),
]
