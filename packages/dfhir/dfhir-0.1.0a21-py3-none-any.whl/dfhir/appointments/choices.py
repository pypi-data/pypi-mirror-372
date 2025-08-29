"""Choices for the appointments app."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AppointmentType(models.TextChoices):
    """Appointment types."""

    ROUTINE = "routine", _("Routine")
    WALK_IN = "walk-in", _("Walk-in")
    CHECKUP = "checkup", _("Check-up")
    FOLLOWUP = "followup", _("Follow-up")
    EMERGENCY = "emergency", _("Emergency")


class AppointmentStatus(models.TextChoices):
    """Appointment statuses."""

    PROPOSED = "proposed", _("Proposed")
    PENDING = "pending", _("Pending")
    BOOKED = "booked", _("Booked")
    ARRIVED = "arrived", _("Arrived")
    FULFILLED = "fulfilled", _("Fulfilled")
    CANCELLED = "cancelled", _("Cancelled")
    NOSHOW = "noshow", _("No Show")
    ENTERED_IN_ERROR = "entered_in_error", _("Entered in Error")
    CHECKED_OUT = "checked_out", _("Checked Out")
    WAITLIST = "waitlist", _("Waitlist")


class AppointmentPriority(models.TextChoices):
    """Appointment priorities."""

    ASAP = "asap", _("ASAP")
    CALLBACK_RESULTS = "callback_results", _("Callback Results")
    ELECTIVE = "elective", _("Elective")
    EMERGENCY = "emergency", _("Emergency")
    PREOP = "preop", _("Preop")
    AS_NEEDED = "as_needed", _("As Needed")
    ROUTINE = "routine", _("Routine")
    RUSH_REPORTING = "rush_reporting", _("Rush Reporting")
    STAT = "stat", _("Stat")
    TIMING_CRITICAL = "timing_critical", _("Timing Critical")
    USE_AS_DIRECTED = "use_as_directed", _("Use As Directed")
    URGENT = "urgent", _("Urgent")
    CALLBACK_FOR_SCHEDULING = "callback_for_scheduling", _("Callback for Scheduling")
    CALLBACK_PLACER_FOR_SCHEDULING = (
        "callback_placer_for_scheduling",
        _("Callback Placer for Scheduling"),
    )
    CONTACT_PATIENT_FOR_SCHEDULING = (
        "contact_patient_for_scheduling",
        _("Contact Patient for Scheduling"),
    )


class RecurrenceType(models.TextChoices):
    """Recurrence types."""

    DAILY = "daily", _("Daily")
    WEEKLY = "weekly", _("Weekly")
    MONTHLY = "monthly", _("Monthly")
    YEARLY = "yearly", _("Yearly")


class ParticipationStatusChoices(models.TextChoices):
    """Participation statuses."""

    ACCEPTED = "accepted", _("Accepted")
    DECLINED = "declined", _("Declined")
    TENTATIVE = "tentative", _("Tentative")
    NEEDSACTION = "needs-action", _("Needs Action")


class WeekOfMonthChoices(models.TextChoices):
    """Week of month choices."""

    FIRST = "first", _("First")
    SECOND = "second", _("Second")
    THIRD = "third", _("Third")
    FOURTH = "fourth", _("Fourth")
    LAST = "last", _("Last")
