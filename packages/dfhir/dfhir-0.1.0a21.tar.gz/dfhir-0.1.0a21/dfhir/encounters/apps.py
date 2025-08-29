"""Encounter app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EncountersConfig(AppConfig):
    """Encounter Configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.encounters"
    verbose_name = _("Encounters")
