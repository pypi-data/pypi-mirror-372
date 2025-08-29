"""immunization recommendations app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImmunizationrecommendationsConfig(AppConfig):
    """app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.immunizationrecommendations"
    verbose_name = _("Immunization Recommendations")
