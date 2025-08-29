"""task model choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class TaskStatusChoices(models.TextChoices):
    """task status choices."""

    DRAFT = "draft", _("Draft")
    REQUESTED = "requested", _("Requested")
    RECEIVED = "received", _("Received")
    ACCEPTED = "accepted", _("Accepted")
    REJECTED = "rejected", _("Rejected")
    READY = "ready", _("Ready")
    CANCELLED = "cancelled", _("Cancelled")
    IN_PROGRESS = "in-progress", _("In Progress")
    OM_HOLD = "on-hold", ("On Hold")
    FAILED = "failed", _("Failed")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class TaskIntentChoices(models.TextChoices):
    """task intent model choices."""

    UNKNOWN = "unknown", _("unknown")
    PROPOSAL = "proposal", _("proposal")
    PLAN = "plan", _("plan")
    ORDER = "order", _("order")
    ORIGINAL_ORDER = "original-order", _("original-order")
    REFLEX_ORDER = "reflex-order", _("reflex-order")
    FILLER_ORDER = "filler-order", _("filler-order")
    INSTANCE_ORDER = "instance-order", _("instance-order")
    OPTION = "option", _("option")


class TaskPriorityChoices(models.TextChoices):
    """task priority choices."""

    ROUTINE = "routine", _("routine")
    URGENT = "urgent", _("urgent")
    ASAP = "asap", _("asap")
    STAT = "stat", _("stat")
