"""Persons app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PersonsConfig(AppConfig):
    """Persons app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.persons"
    verbose_name = _("Persons")
