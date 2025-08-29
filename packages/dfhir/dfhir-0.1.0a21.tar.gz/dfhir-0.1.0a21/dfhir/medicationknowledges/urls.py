"""medication knowledge URL Configuration."""

from django.urls import path

from dfhir.medicationknowledges import views

app_name = "medicationknowledges"
urlpatterns = [
    path("medicationknowledges/", views.MedicationKnowledgeListView.as_view()),
    path(
        "medicationknowledges/<int:pk>/", views.MedicationKnowledgeDetailView.as_view()
    ),
]
