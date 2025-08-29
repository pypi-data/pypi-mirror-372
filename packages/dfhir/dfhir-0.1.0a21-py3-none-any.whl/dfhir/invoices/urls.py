"""Invoice urls."""

from django.urls import path

from . import views

app_name = "invoices"


urlpatterns = [
    path("invoices/", views.InvoiceListView.as_view()),
    path("invoices/<int:pk>/", views.InvoiceDetailView.as_view()),
]
