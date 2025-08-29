"""Practitioners app configuration."""

import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PractitionersConfig(AppConfig):
    """Practitioners app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.practitioners"
    verbose_name = _("Practitioners")

    def ready(self):
        """Import signals."""
        with contextlib.suppress(ImportError):
            import dfhir.practitioners.signals  # noqa: F401
