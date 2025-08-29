"""Schedule app configuration."""

import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ScheduleConfig(AppConfig):
    """Schedule app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.schedules"
    verbose_name = _("Schedules")

    def ready(self):
        """Import signals."""
        with contextlib.suppress(ImportError):
            import dfhir.schedules.signals  # noqa: F401
