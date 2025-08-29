"""medication dispense choices."""

from django.db.models import TextChoices


class MedicationDispenseStatus(TextChoices):
    """medication dispense status choices."""

    PREPARATION = "preparation", "preparation"
    IN_PROGRESS = "in-progress", "in_progress"
    ON_HOLD = "on_hold", "on_hold"
    COMPLETED = "completed", "completed"
    CANCELLED = "cancelled", "cancelled"
    ENTERED_IN_ERROR = "entered-in-error", "entered_in_error"
    STOPPED = "stopped", "stopped"
    DECLINED = "declined", "declined"
    UNKNOWN = "unknown", "unknown"
