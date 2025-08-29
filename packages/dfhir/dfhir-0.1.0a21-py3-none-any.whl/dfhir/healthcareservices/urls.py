"""Healthcare Services URL Configuration."""

from django.urls import path

from . import views

app_name = "healthcareservices"

urlpatterns = [
    path("healthcareservices/", views.HealthcareServiceListView.as_view()),
    path("healthcareservices/<int:pk>/", views.HealthcareServiceDetailView.as_view()),
    path("services/category/", views.ServiceCategoryListView.as_view()),
    path(
        "services/specialty/",
        views.ClinicalSpecialtyValuesetListView.as_view(),
    ),
    path(
        "services/type/",
        views.ServiceTypeListView.as_view(),
    ),
]
