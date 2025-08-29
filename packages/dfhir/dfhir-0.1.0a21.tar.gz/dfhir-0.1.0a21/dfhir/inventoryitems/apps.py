"""inventory item app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InventoryitemsConfig(AppConfig):
    """Inventory items app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.inventoryitems"
    verbose_name = _("Inventory Items")
