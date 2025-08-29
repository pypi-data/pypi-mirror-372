"""Device usage choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceUsageStatus(models.TextChoices):
    """Device usage status choices."""

    ACTIVE = "active", _("Active")
    COMPLETED = "completed", _("Completed")
    NOT_DONE = "not-done", _("Not Done")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    INTENDED = "intended", _("Intended")
    STOPPED = "stopped", _("Stopped")
    ON_HOLD = "on-hold", _("On Hold")
