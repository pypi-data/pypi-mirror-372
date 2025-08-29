"""genomic study urls."""

from django.urls import path

from dfhir.genomicstudies import views

app_name = "genomicstudy"

urlpatterns = [
    path("genomicstudy/", views.GenomicStudyListView.as_view()),
    path("genomicstudy/<int:pk>/", views.GenomicStudyDetailView.as_view()),
]
