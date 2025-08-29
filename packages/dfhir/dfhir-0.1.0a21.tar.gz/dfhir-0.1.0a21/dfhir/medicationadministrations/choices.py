"""medication administration choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class MedicationAdministrationStatus(TextChoices):
    """medication administration status choices."""

    IN_PROGRESS = "in-progress", _("In Progress")
    NOT_DONE = "not-done", _("Not Done")
    ON_HOLD = "on-hold", _("On Hold")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    STOPPED = "stopped", _("Stopped")
    UNKNOWN = "unknown", _("Unknown")
