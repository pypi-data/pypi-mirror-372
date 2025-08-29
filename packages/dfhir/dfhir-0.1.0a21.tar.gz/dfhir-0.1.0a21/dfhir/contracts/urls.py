"""Contract urls."""

from django.urls import path

from . import views

app_name = "contracts"

urlpatterns = [
    path("contracts/", views.ContractListView.as_view()),
    path("contracts/<int:pk>/", views.ContractDetailView.as_view()),
]
