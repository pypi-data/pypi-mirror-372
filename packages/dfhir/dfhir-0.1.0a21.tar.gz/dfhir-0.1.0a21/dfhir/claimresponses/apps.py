"""Claimresponses app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClaimresponsesConfig(AppConfig):
    """Claimresponses app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.claimresponses"
    verbose_name = _("Claim Responses")
