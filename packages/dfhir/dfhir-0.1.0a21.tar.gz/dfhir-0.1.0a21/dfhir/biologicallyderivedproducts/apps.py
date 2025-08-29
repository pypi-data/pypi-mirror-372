"""Biologivally Derived Products App Configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BiologicallyderivedproductsConfig(AppConfig):
    """Biologically Derived Products app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.biologicallyderivedproducts"
    verbose_name = _("Biologically Derived Products")
