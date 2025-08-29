"""Charge items app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChargeitemsConfig(AppConfig):
    """Charge items app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.chargeitems"
    verbose_name = _("Charge Items")
