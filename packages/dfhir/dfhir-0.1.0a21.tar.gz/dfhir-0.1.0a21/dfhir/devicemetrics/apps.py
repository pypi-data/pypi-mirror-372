"""Device Metrics app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DevicemetricsConfig(AppConfig):
    """Device Metrics app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.devicemetrics"
    verbose_name = _("Device Metrics")
