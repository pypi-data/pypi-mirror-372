"""Flag urls."""

from django.urls import path

from . import views

app_name = "flags"

urlpatterns = [
    path("flags/", views.FlagListView.as_view()),
    path("flags/<int:pk>/", views.FlagDetailView.as_view()),
]
