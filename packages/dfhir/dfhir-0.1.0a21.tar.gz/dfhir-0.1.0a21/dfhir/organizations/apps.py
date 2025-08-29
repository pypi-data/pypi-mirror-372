"""Organizations app configuration."""

import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrganizationsConfig(AppConfig):
    """Organizations app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.organizations"
    verbose_name = _("Organizations")

    def ready(self):
        """Import signals."""
        with contextlib.suppress(ImportError):
            import dfhir.organizations.signals  # noqa: F401
