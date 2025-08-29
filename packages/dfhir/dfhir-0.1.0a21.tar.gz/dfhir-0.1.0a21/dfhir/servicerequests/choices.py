"""Service request choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ServiceRequestStatus(models.TextChoices):
    """Service request status choices."""

    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    ON_HOLD = "on_hold", _("On Hold")
    REVOKED = "revoked", _("Revoked")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered_in_error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")


class ServiceRequestIntent(models.TextChoices):
    """Service request intent choices."""

    PROPOSAL = "proposal", _("Proposal")
    PLAN = "plan", _("Plan")
    ORDER = "order", _("Order")
    ORIGINAL_ORDER = "original-order", _("Original Order")
    REFLEX_ORDER = "reflex-order", _("Reflex Order")
    FILLER_ORDER = "filler-order", _("Filler Order")
    INSTANCE_ORDER = "instance-order", _("Instance Order")
    OPTION = "option", _("Option")


class ServiceRequestPriority(models.TextChoices):
    """SErvice request priority choices."""

    ROUTINE = "routine", _("Routine")
    URGENT = "urgent", _("Urgent")
    ASAP = "asap", _("ASAP")
    STAT = "stat", _("Stat")


class ParameterCode(models.TextChoices):
    """parameter code choices."""

    CATHETER_INSERTION = "catheter-insertion", _("Catheter Insertion")
    BODY_ELEVATION = "body-elevation", _("Body Elevation")
    DECVICE_CONFIGURATION = "device-configuration", _("Device Configuration")
    DEVICE_SETTINGS = "device-settings", _("Device Settings")
