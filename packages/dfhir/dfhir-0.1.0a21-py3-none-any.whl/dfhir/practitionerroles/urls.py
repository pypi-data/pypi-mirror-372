"""practitioner role urls."""

from django.urls import path

from dfhir.practitionerroles import views

app_name = "practitionerroles"

urlpatterns = [
    path("practitionerrole/", views.PractitionerRoleListView.as_view()),
    path("practitionerrole/<int:pk>/", views.PractitionerRoleDetailView.as_view()),
    path("practitionerrole/code/", views.PractitionerRoleCodeListView.as_view()),
]
