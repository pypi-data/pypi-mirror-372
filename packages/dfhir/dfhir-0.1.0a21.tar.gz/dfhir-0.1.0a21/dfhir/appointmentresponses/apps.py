"""Appointment responses app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppointmentresponsesConfig(AppConfig):
    """Appointment responses app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.appointmentresponses"
    verbose_name = _("Appointment Responses")
