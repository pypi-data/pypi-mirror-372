"""Enrollment Requests App Configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EnrollmentrequestsConfig(AppConfig):
    """Enrollment Requests App Configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.enrollmentrequests"
    verbose_name = _("Enrollment Requests")
