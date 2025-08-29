"""medication knowledges app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MedicationknowledgesConfig(AppConfig):
    """Medication Knowledges app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.medicationknowledges"
    verbose_name = _("Medication Knowledges")
