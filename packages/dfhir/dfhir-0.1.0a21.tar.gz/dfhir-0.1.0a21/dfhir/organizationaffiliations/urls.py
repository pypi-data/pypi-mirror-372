"""organization affiliation urls."""

from django.urls import path

from dfhir.organizationaffiliations.views import (
    OrganizationAffiliationDetailview,
    OrganizationAffiliationListview,
)

app_name = "organizationaffiliations"

urlpatterns = [
    path(
        "organizationaffiliations/",
        OrganizationAffiliationListview.as_view(),
        name="organizationaffiliations-list",
    ),
    path(
        "organizationaffiliations/<int:pk>/",
        OrganizationAffiliationDetailview.as_view(),
        name="organizationaffiliations-detail",
    ),
]
