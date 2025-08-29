"""Slots app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SlotsConfig(AppConfig):
    """App configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.slots"
    verbose_name = _("Slots")
