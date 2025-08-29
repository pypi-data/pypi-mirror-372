"""EnrollmentRequests URL Configuration."""

from django.urls import path

from . import views

app_name = "enrollmentrequests"

urlpatterns = [
    path(
        "enrollmentrequests/",
        views.EnrollmentRequestListView.as_view(),
        name="list-create",
    ),
    path(
        "enrollmentrequests/<int:pk>/",
        views.EnrollmentRequestDetailView.as_view(),
        name="detail",
    ),
]
