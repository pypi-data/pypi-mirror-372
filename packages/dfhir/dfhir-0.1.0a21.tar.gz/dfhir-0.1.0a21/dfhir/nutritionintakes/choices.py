"""nutrition intake model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class NutritionIntakeStatusChoices(TextChoices):
    """Nutrition intake status choices."""

    PREPARATION = "preparation", _("Preparation")
    IN_PROGRESS = "in-progress", _("In Progress")
    NOT_DONE = "not-done", _("Not Done")
    ONE_HOLD = "on-hold", _("On Hold")
    STOPPED = "stopped", _("Stopped")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")
