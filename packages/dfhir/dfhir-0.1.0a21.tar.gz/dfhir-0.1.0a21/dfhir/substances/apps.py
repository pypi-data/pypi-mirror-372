"""Substances app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubstancesConfig(AppConfig):
    """Substances app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.substances"
    verbose_name = _("Substances")
