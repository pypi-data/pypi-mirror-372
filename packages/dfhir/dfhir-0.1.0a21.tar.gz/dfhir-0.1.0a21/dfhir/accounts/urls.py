"""Accounts Urls."""

from django.urls import path

from . import views

app_name = "accounts"


urlpatterns = [
    path("accounts/", views.AccountListView.as_view()),
    path("accounts/<int:pk>/", views.AccountDetailView.as_view()),
]
