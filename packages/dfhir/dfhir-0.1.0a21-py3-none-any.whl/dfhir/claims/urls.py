"""Claims urls."""

from django.urls import path

from . import views

app_name = "claims"

urlpatterns = [
    path("claims/", views.ClaimListView.as_view()),
    path("claims/<int:pk>/", views.ClaimDetailView.as_view()),
]
