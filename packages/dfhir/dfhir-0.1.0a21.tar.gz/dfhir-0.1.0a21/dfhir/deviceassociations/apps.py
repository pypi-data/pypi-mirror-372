"""Deviceassociations app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DeviceassociationsConfig(AppConfig):
    """Deviceassociations app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.deviceassociations"
    verbose_name = _("deviceassociations")
