"""medication statements app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MedicationstatementsConfig(AppConfig):
    """medication statements app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.medicationstatements"
    verbose_name = _("Medication Statements")
