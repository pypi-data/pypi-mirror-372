"""nutrition intake urls."""

from django.urls import path

from dfhir.nutritionintakes.views import (
    NutritionIntakeDetailView,
    NutritionIntakeListView,
)

app_name = "nutritionintakes"


urlpatterns = [
    path("nutritionintakes/", NutritionIntakeListView.as_view(), name="list"),
    path(
        "nutritionintakes/<int:pk>/", NutritionIntakeDetailView.as_view(), name="detail"
    ),
]
