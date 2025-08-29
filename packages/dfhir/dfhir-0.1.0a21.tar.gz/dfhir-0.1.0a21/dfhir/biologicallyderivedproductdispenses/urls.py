"""biologically derived product dispenses urls."""

from django.urls import path

from dfhir.biologicallyderivedproductdispenses import views

app_name = "biologicallyderivedproductdispenses"


urlpatterns = [
    path(
        "biologicallyderivedproductdispenses/",
        views.BiologicallyDerivedProductDispenseListView.as_view(),
    ),
    path(
        "biologicallyderivedproductdispenses/<int:pk>/",
        views.BiologicallyDerivedProductDispenseDetailView.as_view(),
    ),
]
