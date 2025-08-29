"""transport choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class TransportStatusChoices(models.TextChoices):
    """transport status choices."""

    PREPARATION = "preparation", _("Preparation")
    IN_PROGRESS = "in-progress", _("In Progress")
    NOT_DONE = "not-done", _("Not Done")
    SUSPENDED = "suspended", _("Suspended")
    STOPPED = "stopped", _("Stopped")
    ON_HOLD = "on-hold", _("On Hold")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")
