"""Slot choices for the slots app."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AppointmentType(models.TextChoices):
    """Appointment type choices."""

    WALK_IN = "walk-in", _("Walk-in")
    ROUTINE = "routine", _("Routine")
    CHECKUP = "checkup", _("Check-up")
    FOLLOWUP = "followup", _("Follow-up")
    EMERGENCY = "emergency", _("Emergency")


class SlotStatus(models.TextChoices):
    """Slot status choices."""

    FREE = "free", _("Free")
    BUSY = "busy", _("Busy")
    BUSY_UNAVAILABLE = "busy-unavailable", _("Busy Unavailable")
    BUSY_TENTATIVE = "busy-tentative", _("Busy Tentative")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
