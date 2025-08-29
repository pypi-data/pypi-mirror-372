"""Slots URL Configuration."""

from django.urls import path

from . import views

app_name = "slots"

urlpatterns = [
    path("slots/", views.SlotListView.as_view(), name="slot-list"),
    path("slots/<int:pk>/", views.SlotDetailView.as_view(), name="slot-detail"),
]
