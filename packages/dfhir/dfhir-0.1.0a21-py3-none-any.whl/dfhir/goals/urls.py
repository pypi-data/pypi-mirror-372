"""Goals urls."""

from django.urls import path

from . import views

app_name = "goals"

urlpatterns = [
    path("goals/", views.GoalListView.as_view(), name="list_view"),
    path("goals/<int:pk>/", views.GoalDetailView.as_view(), name="detail_view"),
]
