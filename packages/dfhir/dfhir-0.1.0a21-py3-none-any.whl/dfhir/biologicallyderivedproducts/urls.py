"""Biologically Derived Products URL Configuration."""

from django.urls import path

from . import views

app_name = "biologicallyderivedproducts"

urlpatterns = [
    path(
        "biologicallyderivedproducts/",
        views.BiologicallyDerivedProductListView.as_view(),
    ),
    path(
        "biologicallyderivedproducts/<int:pk>/",
        views.BiologicallyDerivedProductDetailView.as_view(),
    ),
]
