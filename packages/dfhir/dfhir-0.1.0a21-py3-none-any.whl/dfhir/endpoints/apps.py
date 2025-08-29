"""Endpoints app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EndpointsConfig(AppConfig):
    """Endpoints app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.endpoints"
    verbose_name = _("Endpoints")
