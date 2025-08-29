"""Locations URL Configuration."""

from django.urls import path

from .views import LocationDetail, LocationList

app_name = "locations"

urlpatterns = [
    path("locations/", LocationList.as_view(), name="location_list"),
    path("locations/<int:pk>/", LocationDetail.as_view(), name="location_detail"),
]
