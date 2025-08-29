"""supply delivery choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class SupplyDeliveryStatusChoices(models.TextChoices):
    """supply delivery status choices."""

    IN_PROGRESS = "in-progress", _("In Progress")
    COMPLETED = "completed", _("Completed")
    ABANDONED = "abandoned", _("Abandoned")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered In Error")
