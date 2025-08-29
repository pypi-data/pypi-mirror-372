"""Detected issues app config."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DetectedissuesConfig(AppConfig):
    """Detected issues app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.detectedissues"
    verbose_name = _("Detected Issues")
