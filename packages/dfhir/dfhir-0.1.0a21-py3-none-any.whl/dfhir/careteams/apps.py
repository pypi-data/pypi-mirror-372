"""Care Teams app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CareteamsConfig(AppConfig):
    """Care Teams app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.careteams"
    verbose_name = _("Care Teams")
