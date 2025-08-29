"""Device definitions urls."""

from django.urls import path

from . import views

app_name = "devicedefinitions"

urlpatterns = [
    path(
        "devicedefinitions/",
        views.DeviceDefinitionListCreateView.as_view(),
        name="list-create",
    ),
    path(
        "devicedefinitions/<int:pk>/",
        views.DeviceDefinitionDetailView.as_view(),
        name="detail",
    ),
]
