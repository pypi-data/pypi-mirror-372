"""Device Definition choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceDefinitionRegulatoryIdentifierType(models.TextChoices):
    """Device Definition Regulatory Identifier Type choices."""

    BASIC = "BASIC", _("basic")
    MASTER = "MASTER", _("master")
    LICENSE = "LICENSE", _("license")


class DeviceDefinitionCorrectiveActionScope(models.TextChoices):
    """Device Definition Corrective Action Scope choices."""

    MODEL = "model", _("model")
    LOT_NUMBERS = "lot_numbers", _("lot_numbers")
    SERIAL_NUMBERS = "serial_numbers", _("serial_numbers")
