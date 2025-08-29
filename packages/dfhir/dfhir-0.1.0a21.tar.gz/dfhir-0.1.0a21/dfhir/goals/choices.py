"""Goals choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class GoalLifecycleStatusChoices(models.TextChoices):
    """Goal Life Cycle status choices."""

    PROPOSED = "proposed", _("Proposed")
    PLANNED = "planned", _("Planned")
    ACCEPTED = "accepted", _("Accepted")
    ACTIVE = "active", _("Active")
    ON_HOLD = "on-hold", _("On Hold")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    REJECTED = "rejected", _("Rejected")


class GoalAcceptanceStatusChoices(models.TextChoices):
    """Goal Acceptance Status choices."""

    AGREE = "agree", _("Agree")
    DISAGREE = "disagree", _("Disagree")
    PENDING = "pending", _("Pending")
