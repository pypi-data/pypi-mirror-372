"""Appointment responses choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AppointmentResponseParticipantStatusChoices(models.TextChoices):
    """Appointment response participant status choices."""

    ACCEPTED = "accepted", _("Accepted")
    DECLINED = "declined", _("Declined")
    TENTATIVE = "tentative", _("Tentative")
    NEEDS_ACTION = "needs-action", _("Needs Action")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
