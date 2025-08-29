"""medication requests app config."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MedicationrequestsConfig(AppConfig):
    """app configurations."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.medicationrequests"
    verbose_name = _("Medication Requests")
