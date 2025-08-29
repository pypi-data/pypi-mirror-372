"""Specimen definitions App configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SpecimendefinitionsConfig(AppConfig):
    """Specimen definitions config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.specimendefinitions"
    verbose_name = _("Specimen Definitions")
