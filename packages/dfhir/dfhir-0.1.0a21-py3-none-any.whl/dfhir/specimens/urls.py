"""specimen urls."""

from django.urls import path

from dfhir.specimens import views

app_name = "specimens"


urlpatterns = [
    path("specimens/", views.SpecimenListView.as_view()),
    path("specimens/<int:pk>/", views.SpecimenDetailView.as_view()),
]
