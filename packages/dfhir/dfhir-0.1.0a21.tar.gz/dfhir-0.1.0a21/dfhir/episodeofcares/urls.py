"""Episode of care urls."""

from django.urls import path

from . import views

app_name = "episodeofcares"

urlpatterns = [
    path("episodeofcares/", views.EpisodeOfCareListView.as_view()),
    path("episodeofcares/<int:pk>/", views.EpisodeOfCareDetailView.as_view()),
]
