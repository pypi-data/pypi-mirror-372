"""supply request choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class SupplyRequestStatusChoices(models.TextChoices):
    """supply request status choices."""

    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    SUSPENDED = "suspended", _("Suspended")
    CANCELLED = "cancelled", _("Cancelled")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in error")
    UNKNOWN = "unknown", _("Unknown")


class SupplyRequestIntentChoices(models.TextChoices):
    """supply request intent choices."""

    PROPOSAL = "proposal", _("Proposal")
    PLAN = "plan", _("Plan")
    DIRECTIVE = "directive", _("Directive")
    ORDER = "order", _("Order")
    ORIGINAL_ORDER = "original-order", _("Original Order")
    REFLEX_ORDER = "reflex-order", _("Reflex Order")
    FILLER_ORDER = "filler-order", _("Filler Order")
    INSTANCE_ORDER = "instance-order", _("Instance Order")
    OPTION = "option", _("Option")


class SupplyRequestPriorityChoices(models.TextChoices):
    """supply request priority choices."""

    ROUTINE = "routine", _("Routine")
    URGENT = "urgent", _("Urgent")
    STAT = "stat", _("Stat")
    ASAP = "asap", _("ASAP")
