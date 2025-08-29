"""inventory report urls."""

from django.urls import path

from dfhir.inventoryreports import views

app_name = "inventoryreports"

urlpatterns = [
    path(
        "inventoryreports/",
        views.InventoryReportListView.as_view(),
        name="inventoryreport-list",
    ),
    path(
        "inventoryreports/<int:pk>/",
        views.InventoryReportDetailView.as_view(),
        name="inventoryreport-list",
    ),
]
