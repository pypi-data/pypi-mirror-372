"""specimen model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class SpecimenStatus(TextChoices):
    """specimen status choices."""

    AVAILABLE = "available", _("Available")
    UNAVAILABLE = "unavailable", _("Unavailable")
    UNSATISFACTORY = "unsatisfactory", _("Unsatisfactory")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class SpecimenCombinedChoices(TextChoices):
    """specimen combined choices."""

    GROUPED = "grouped", _("Grouped")
    POOLED = "pooled", _("Pooled")
