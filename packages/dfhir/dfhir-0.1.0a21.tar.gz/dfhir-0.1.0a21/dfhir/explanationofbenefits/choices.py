"""Explanation of Benefits Choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ExplanationOfBenefitStatus(models.TextChoices):
    """Explanation of Benefit Status Choices."""

    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    DRAFT = "draft", _("Draft")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")


class ExplanationOfBenefitUse(models.TextChoices):
    """Explanation of Benefit Use Choices."""

    CLAIM = "claim", _("Claim")
    PREAUTHORIZATION = "preauthorization", _("Preauthorization")
    PREDETERMINATION = "predetermination", _("Predetermination")


class ExplanationOfBenefitOutcome(models.TextChoices):
    """Explanation of Benefit Outcome Choices."""

    QUEUED = "queued", _("Queued")
    COMPLETE = "complete", _("Complete")
    ERROR = "error", _("Error")
    PARTIAL = "partial", _("Partial")
