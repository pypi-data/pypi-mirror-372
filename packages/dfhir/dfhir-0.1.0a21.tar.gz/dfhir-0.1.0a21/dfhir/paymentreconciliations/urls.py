"""payment reconciliations URL Configuration."""

from django.urls import path

from dfhir.paymentreconciliations import views

app_name = "paymentreconciliations"

urlpatterns = [
    path("paymentreconciliations/", views.PaymentReconciliationListView.as_view()),
    path(
        "paymentreconciliations/<int:pk>/",
        views.PaymentReconciliationDetailView.as_view(),
    ),
]
