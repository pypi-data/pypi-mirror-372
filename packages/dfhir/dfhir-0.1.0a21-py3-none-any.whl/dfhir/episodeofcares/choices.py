"""Choices for EpisodeOfCare model."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class EpisodeOfCareStatusChoices(models.TextChoices):
    """Choices for EpisodeOfCare status."""

    PLANNED = "planned", _("Planned")
    WAITLIST = "waitlist", _("Waitlist")
    ACTIVE = "active", _("Active")
    ONHOLD = "onhold", _("On Hold")
    FINISHED = "finished", _("Finished")
    CANCELLED = "cancelled", _("Cancelled")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
