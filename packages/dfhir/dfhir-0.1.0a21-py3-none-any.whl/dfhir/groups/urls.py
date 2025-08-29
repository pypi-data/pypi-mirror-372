"""Group Urls."""

from django.urls import path

from . import views

app_name = "groups"

urlpatterns = [
    path("groups/", views.GroupListView.as_view()),
    path("groups/<int:pk>/", views.GroupDetailView.as_view()),
]
