"""condition urls."""

from django.urls import path

from dfhir.conditions.views import ConditionDetailView, ConditionListView

app_name = "conditions"

urlpatterns = [
    path("conditions/", ConditionListView.as_view(), name="condition-list"),
    path(
        "conditions/<int:pk>/", ConditionDetailView.as_view(), name="condition-detail"
    ),
]
