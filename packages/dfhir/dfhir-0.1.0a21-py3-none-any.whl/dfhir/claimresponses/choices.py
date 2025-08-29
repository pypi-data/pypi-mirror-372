"""Claim responses choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ClaimResponseStatus(models.TextChoices):
    """Claim response status choices."""

    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    DRAFT = "draft", _("Draft")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class ClaimResponseOutcome(models.TextChoices):
    """Claim response outcome choices."""

    QUEUED = "queued", _("Queued")
    COMPLETE = "complete", _("Complete")
    ERROR = "error", _("Error")
    PARTIAL = "partial", _("Partial")


class ClaimResponseUse(models.TextChoices):
    """Claim response use choices."""

    CLAIM = "claim", _("Claim")
    PREAUTHORIZATION = "preauthorization", _("Preauthorization")
    PREDETERMINATION = "predetermination", _("Predetermination")
