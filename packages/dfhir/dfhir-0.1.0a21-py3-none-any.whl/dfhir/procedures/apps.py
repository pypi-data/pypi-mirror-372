"""Procedures app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProceduresConfig(AppConfig):
    """procedures app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.procedures"
    verbose_name = _("Procedures")
