"""Detected issues choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DetectedIssueStatusChoices(models.TextChoices):
    """Detected issue status choices."""

    PRELIMINARY = "preliminary", _("Preliminary")
    FINAL = "final", _("Final")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    MITIGATED = "mitigated", _("Mitigated")


class DetectedIssueSeverityChoices(models.TextChoices):
    """Detected issue severity choices."""

    HIGH = "high", _("High")
    MODERATE = "moderate", _("Moderate")
    LOW = "low", _("Low")
