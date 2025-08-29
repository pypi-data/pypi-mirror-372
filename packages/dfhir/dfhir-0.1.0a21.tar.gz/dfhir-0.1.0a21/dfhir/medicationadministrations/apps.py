"""medication administrations app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MedicationadministrationsConfig(AppConfig):
    """medication administrations app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.medicationadministrations"
    verbose_name = _("Medication Administrations")
