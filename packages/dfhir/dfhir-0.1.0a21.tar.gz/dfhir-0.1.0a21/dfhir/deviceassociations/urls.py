"""Deviceassociations urls."""

from django.urls import path

from . import views

app_name = "deviceassociations"


urlpatterns = [
    path("deviceassociations/", views.DeviceAssociationListView.as_view()),
    path("deviceassociations/<int:pk>/", views.DeviceAssociationDetailView.as_view()),
]
