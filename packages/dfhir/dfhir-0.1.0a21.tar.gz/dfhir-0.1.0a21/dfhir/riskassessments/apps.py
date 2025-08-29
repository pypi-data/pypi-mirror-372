"""risk assessment app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RiskassessmentsConfig(AppConfig):
    """Risk assessments app Config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.riskassessments"
    verbose_name = _("Risk Assessments")
