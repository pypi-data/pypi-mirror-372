"""EnrollmentResponses URL Configuration."""

from django.urls import path

from . import views

app_name = "enrollmentresponses"

urlpatterns = [
    path("enrollmentresponses/", views.EnrollmentResponseListView.as_view()),
    path("enrollmentresponses/<int:pk>/", views.EnrollmentResponseDetailView.as_view()),
]
