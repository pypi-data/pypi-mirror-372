"""nutrition orders urls."""

from django.urls import path

from dfhir.nutritionorders.views import (
    NutritionOrderDetailView,
    NutritionOrderListView,
)

app_name = "nutritionorders"

urlpatterns = [
    path(
        "nutritionorders/",
        NutritionOrderListView.as_view(),
        name="nutrition-order-list",
    ),
    path(
        "nutritionorders/<int:pk>/",
        NutritionOrderDetailView.as_view(),
        name="nutrition-order-detail",
    ),
]
