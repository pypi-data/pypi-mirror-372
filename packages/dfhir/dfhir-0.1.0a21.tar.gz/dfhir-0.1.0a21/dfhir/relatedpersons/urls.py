"""Related Patient URL Configuration."""

from django.urls import path

from . import views

app_name = "relatedpersons"

urlpatterns = [
    path("relatedpersons/", views.RelatedPersonListView.as_view()),
    path("relatedpersons/<int:pk>/", views.RelatedPersonDetailView.as_view()),
]
