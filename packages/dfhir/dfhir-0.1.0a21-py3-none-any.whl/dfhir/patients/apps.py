"""Patients app configuration."""

import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PatientsConfig(AppConfig):
    """Patients app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.patients"
    verbose_name = _("Patients")

    def ready(self):
        """Import signals."""
        with contextlib.suppress(ImportError):
            import dfhir.patients.signals  # noqa: F401
