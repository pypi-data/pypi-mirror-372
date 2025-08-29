"""Healthcareservices app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HealthcareservicesConfig(AppConfig):
    """Healthcareservices app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.healthcareservices"
    verbose_name = _("Healthcareservices")
