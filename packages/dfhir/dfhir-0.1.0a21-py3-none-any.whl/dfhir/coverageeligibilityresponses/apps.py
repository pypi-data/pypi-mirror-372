"""Coverage Eligibility Responses App Configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoverageeligibilityresponsesConfig(AppConfig):
    """Coverage Eligibility Responses App Configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.coverageeligibilityresponses"
    verbose_name = _("Coverage Eligibility Responses")
