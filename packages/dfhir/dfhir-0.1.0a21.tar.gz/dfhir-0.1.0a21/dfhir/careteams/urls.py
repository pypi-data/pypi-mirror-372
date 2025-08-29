"""CareTeam URL Configuration."""

from django.urls import path

from . import views

app_name = "careteams"

urlpatterns = [
    path("careteams/", views.CareTeamListView.as_view()),
    path("careteams/<int:pk>/", views.CareTeamDetailView.as_view()),
]
