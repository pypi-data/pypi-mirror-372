"""inventory item urls."""

from django.urls import path

from dfhir.inventoryitems.views import InventoryItemDetailView, InventoryItemListView

app_name = "inventoryitems"

urlpatterns = [
    path("inventoryitems/", InventoryItemListView.as_view(), name="inventoryitem-list"),
    path(
        "inventoryitems/<int:pk>/",
        InventoryItemDetailView.as_view(),
        name="inventoryitem-detail",
    ),
]
