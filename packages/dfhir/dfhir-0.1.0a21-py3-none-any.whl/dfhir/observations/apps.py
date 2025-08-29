"""observation app configuration module."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ObservationsConfig(AppConfig):
    """Observations app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.observations"
    verbose_name = _("Observations")
