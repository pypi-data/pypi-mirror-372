"""{{ camel_case_app_name }} choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceRequestStatus(models.TextChoices):
    """Device Request status choices."""

    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    ON_HOLD = "on-hold", _("On Hold")
    REVOKED = "revoked", _("Revoked")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")


class DeviceRequestIntent(models.TextChoices):
    """Device Request intent choices."""

    PROPOSAL = "proposal", _("Proposal")
    PLAN = "plan", _("Plan")
    ORDER = "order", _("Order")
    ORIGINAL_ORDER = "original-order", _("Original Order")
    REFLEX_ORDER = "reflex-order", _("Reflex Order")
    FILLER_ORDER = "filler-order", _("Filler Order")
    INSTANCE_ORDER = "instance-order", _("Instance Order")
    OPTION = "option", _("Option")


class DeviceRequestPriority(models.TextChoices):
    """Device Request priority choices."""

    ROUTINE = "routine", _("Routine")
    URGENT = "urgent", _("Urgent")
    STAT = "stat", _("Stat")
    ASAP = "asap", _("Asap")
