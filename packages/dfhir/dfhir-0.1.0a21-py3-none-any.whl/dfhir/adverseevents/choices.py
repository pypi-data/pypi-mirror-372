"""Advere Event choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AdverseEventStatusChoices(models.TextChoices):
    """Adverse Event status choices."""

    IN_PROGRESS = "in-progress", _("in-progress")
    COMPLETED = "completed", _("completed")
    ENTERED_IN_ERROR = "entered-in-error", _("entered-in-error")
    UNKNOWN = "unknown", _("unknown")


class AdverseEventActualityChoices(models.TextChoices):
    """Adverse Event actuality choices."""

    ACTUAL = "actual", _("actual")
    POTENTIAL = "potential", _("potential")
