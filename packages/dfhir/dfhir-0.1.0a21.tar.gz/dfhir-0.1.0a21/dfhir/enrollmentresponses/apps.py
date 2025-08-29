"""Enrollment Responses App Configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EnrollmentresponsesConfig(AppConfig):
    """Enrollment Responses App Configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.enrollmentresponses"
    verbose_name = _("Enrollment Responses")
