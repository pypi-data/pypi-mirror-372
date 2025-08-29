"""DeviceDispenses choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceDispenseStatus(models.TextChoices):
    """DeviceDispenseStatus choices."""

    IN_PROGRESS = "in-progress", _("In Progress")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    STOPPED = "stopped", _("Stopped")
    ON_HOLD = "on-hold", _("On Hold")
    CANCELLED = "cancelled", _("Cancelled")
    PREPARATION = "preparation", _("Preparation")
    DECLINED = "declined", _("Declined")
