"""formulary item app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FormularyitemsConfig(AppConfig):
    """Formulary items app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.formularyitems"
    verbose_name = _("Formulary Items")
