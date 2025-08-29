"""supply requests urls."""

from django.urls import path

from dfhir.supplyrequests import views

app_name = "supplyrequests"

urlpatterns = [
    path("supplyrequests/", views.SupplyRequestListView.as_view(), name="list"),
    path(
        "supplyrequests/<int:pk>/",
        views.SupplyRequestDetailView.as_view(),
        name="detail",
    ),
]
