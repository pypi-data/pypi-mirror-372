"""Organizations URL Configuration."""

from django.urls import path

from . import views

app_name = "organizations"

urlpatterns = [
    path("organizations/", views.OrganizationListView.as_view()),
    path("organizations/<int:pk>/", views.OrganizationDetailView.as_view()),
]
