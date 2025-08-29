"""Family member history urls."""

from django.urls import path

from . import views

app_name = "familymemberhistories"

# TODO: we should consider <uuid:pk> instead of <int:pk> for the primary key of all routes.

urlpatterns = [
    path(
        "familymemberhistories/",
        views.FamilyMemberHistoryListView.as_view(),
        name="familymemberhistory-list",
    ),
    path(
        "familymemberhistories/<int:pk>/",
        views.FamilyMemberHistoryDetailView.as_view(),
        name="familymemberhistory-detail",
    ),
]
