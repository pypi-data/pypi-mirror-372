"""Adverse events app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AdverseeventsConfig(AppConfig):
    """Adverse events app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.adverseevents"
    verbose_name = _("Adverse Events")
