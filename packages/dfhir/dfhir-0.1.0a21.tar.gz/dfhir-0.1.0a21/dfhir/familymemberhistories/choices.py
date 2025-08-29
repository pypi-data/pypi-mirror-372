"""Family Member History choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class FamilyMemberHistoryStatus(models.TextChoices):
    """Family Member History status choices."""

    PARTIAL = "partial", _("Partial")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    HEALTH_UNKNOWN = "health-unknown", _("Health Unknown")
