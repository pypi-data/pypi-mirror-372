"""Device choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceStatus(models.TextChoices):
    """Device status choices."""

    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
