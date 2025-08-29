"""tasks urls."""

from django.urls import path

from dfhir.tasks import views

app_name = "tasks"

urlpatterns = [
    path("tasks/", views.TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", views.TaskDetailView.as_view(), name="task-detail"),
]
