"""Coverage Eligibility Request App Configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoverageeligibilityrequestsConfig(AppConfig):
    """Coverage Eligibility Request App Configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.coverageeligibilityrequests"
    verbose_name = _("Coverage Eligibility Request")
