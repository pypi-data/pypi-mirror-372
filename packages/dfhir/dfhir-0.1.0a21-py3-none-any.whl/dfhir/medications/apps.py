"""medications app configurations."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MedicationsConfig(AppConfig):
    """medications app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.medications"
    verbose_name = _("Medications")
