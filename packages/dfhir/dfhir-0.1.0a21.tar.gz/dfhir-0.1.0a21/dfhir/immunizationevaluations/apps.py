"""immunization evaluations app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImmunizationevaluationsConfig(AppConfig):
    """immunization evaluations app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.immunizationevaluations"
    verbose_name = _("Immunization Evaluations")
