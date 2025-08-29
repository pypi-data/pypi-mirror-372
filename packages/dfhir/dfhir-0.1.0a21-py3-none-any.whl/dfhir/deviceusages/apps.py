"""Device usage apps."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DeviceusagesConfig(AppConfig):
    """Device usage config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.deviceusages"
    verbose_name = _("Device Usages")
