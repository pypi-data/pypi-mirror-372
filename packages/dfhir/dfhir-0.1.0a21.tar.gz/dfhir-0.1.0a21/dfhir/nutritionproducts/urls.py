"""Nutrition Product."""

from django.urls import path

from . import views

app_name = "nutritionproducts"

urlpatterns = [
    path("nutritionproducts/", views.NutritionProductListView.as_view()),
    path("nutritionproducts/<int:pk>/", views.NutritionProductDetailView.as_view()),
]
