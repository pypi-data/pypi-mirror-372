"""provenances URLs."""

from django.urls import path

from dfhir.provenances import views

app_name = "provenances"

urlpatterns = [
    path("provenances/", views.ProvenanceListView.as_view()),
    path("provenances/<int:pk>/", views.ProvenanceDetailView.as_view()),
]
