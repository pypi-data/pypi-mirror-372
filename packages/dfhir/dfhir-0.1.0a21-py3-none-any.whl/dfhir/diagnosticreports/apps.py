"""diagnostic report app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DiagnosticreportsConfig(AppConfig):
    """diagnostic report app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.diagnosticreports"
    verbose_name = _("Diagnostic Reports")
