"""biologically derived product dispenses app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BiologicallyderivedproductdispensesConfig(AppConfig):
    """app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.biologicallyderivedproductdispenses"
    verbose_name = _("Biologically Derived Product Dispenses")
