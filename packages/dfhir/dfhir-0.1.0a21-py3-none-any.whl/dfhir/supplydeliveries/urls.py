"""supply delivery urls."""

from django.urls import path

from dfhir.supplydeliveries import views

app_name = "supplydelivery"

urlpatterns = [
    path("supplydelivery/", views.SupplyDeliveryListView.as_view()),
    path("supplydelivery/<int:pk>/", views.SupplyDeliveryDetailedView.as_view()),
]
