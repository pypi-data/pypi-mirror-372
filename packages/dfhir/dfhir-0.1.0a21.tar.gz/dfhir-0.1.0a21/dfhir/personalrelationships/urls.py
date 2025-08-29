"""Personal Relationship Target Reference urls."""

from django.urls import path

from . import views

app_name = "personalrelationships"

urlpatterns = [
    path(
        "personalrelationships/",
        views.PersonalRelationshipListView.as_view(),
    ),
    path(
        "personalrelationships/<int:pk>/",
        views.PersonalRelationshipDetailView.as_view(),
    ),
]
