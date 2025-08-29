"""inventory reports app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InventoryreportsConfig(AppConfig):
    """Inventory reports config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.inventoryreports"
    verbose_name = _("Inventory Reports")
