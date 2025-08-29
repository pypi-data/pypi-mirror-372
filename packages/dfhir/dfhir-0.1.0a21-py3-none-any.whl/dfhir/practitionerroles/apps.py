"""practitioner role app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PractitionerrolesConfig(AppConfig):
    """practitionerrole app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.practitionerroles"
    verbose_name = _("Practitioner Role")
