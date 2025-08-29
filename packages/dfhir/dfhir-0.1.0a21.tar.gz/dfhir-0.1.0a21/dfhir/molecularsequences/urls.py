"""molecular sequences urls."""

from django.urls import path

from dfhir.molecularsequences import views

app_name = "molecularsequences"

urlpatterns = [
    path("molecularsequences/", views.MolecularSequenceListView.as_view()),
    path("molecularsequences/<int:pk>/", views.MolecularSequenceDetailView.as_view()),
]
