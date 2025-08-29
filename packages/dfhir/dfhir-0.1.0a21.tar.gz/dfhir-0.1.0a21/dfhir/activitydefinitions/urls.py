"""activity definition urls."""

from django.urls import path

from dfhir.activitydefinitions import views

app_name = "activitydefinitions"

urlpatterns = [
    path("activitydefinitions/", views.ActivityDefinitionListView.as_view()),
    path(
        "activitydefinitions/<int:pk>/",
        views.ActivityDefinitionDetailView.as_view(),
    ),
]
