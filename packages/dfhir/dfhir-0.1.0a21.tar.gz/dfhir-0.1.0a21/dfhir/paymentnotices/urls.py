"""Payment Notice URL configuration."""

from django.urls import path

from . import views

app_name = "paymentnotices"

urlpatterns = [
    path("paymentnotices/", views.PaymentNoticeListView.as_view()),
    path("paymentnotices/<int:pk>/", views.PaymentNoticeDetailView.as_view()),
]
