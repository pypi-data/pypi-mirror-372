"""Devices app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DevicesConfig(AppConfig):
    """Devices app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.devices"
    verbose_name = _("Devices")
