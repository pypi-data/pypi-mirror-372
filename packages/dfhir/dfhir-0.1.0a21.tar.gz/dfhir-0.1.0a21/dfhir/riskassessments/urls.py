"""risk assessment urls."""

from django.urls import path

from dfhir.riskassessments.views import (
    RiskAssessmentDetialView,
    RiskManagementListView,
)

app_name = "riskassessments"

urlpatterns = [
    path(
        "riskassessments/",
        RiskManagementListView.as_view(),
        name="risk_management_list",
    ),
    path(
        "riskassessments/<int:pk>/",
        RiskAssessmentDetialView.as_view(),
        name="risk_assessment_detail",
    ),
]
