"""communications app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommunicationsConfig(AppConfig):
    """Communications app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.communications"
    verbose_name = _("Communications")
