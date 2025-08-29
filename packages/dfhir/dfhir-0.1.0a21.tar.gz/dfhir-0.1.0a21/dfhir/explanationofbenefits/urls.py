"""Explanation of Benefits URL Configuration."""

from django.urls import path

from . import views

app_name = "explanationofbenefits"


urlpatterns = [
    path("explanationofbenefits/", views.ExplanationOfBenefitListView.as_view()),
    path(
        "explanationofbenefits/<int:pk>/",
        views.ExplanationOfBenefitDetailView.as_view(),
    ),
]
