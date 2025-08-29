"""Coverages app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoveragesConfig(AppConfig):
    """Coverages app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.coverages"
    verbose_name = _("Coverages")
