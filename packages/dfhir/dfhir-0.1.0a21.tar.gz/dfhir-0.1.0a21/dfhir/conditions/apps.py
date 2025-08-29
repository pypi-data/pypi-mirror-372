"""Conditions app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ConditionsConfig(AppConfig):
    """Conditions app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.conditions"
    verbose_name = _("Conditions")
