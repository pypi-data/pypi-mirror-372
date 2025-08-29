"""Care plan urls."""

from django.urls import path

from . import views

app_name = "careplans"


urlpatterns = [
    path("careplans/", views.CarePlanListView.as_view()),
    path("careplans/<int:pk>/", views.CarePlanDetailView.as_view()),
]
