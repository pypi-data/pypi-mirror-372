"""Enrollment responses choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class EnrollmentResponseStatus(models.TextChoices):
    """Enrollment response status choices."""

    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    DRAFT = "draft", _("Draft")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class EnrollmentResponseOutcome(models.TextChoices):
    """Enrollment response outcome choices."""

    QUEUED = "queued", _("Queued")
    COMPLETE = "complete", _("Complete")
    ERROR = "error", _("Error")
    PARTIAL = "partial", _("Partial")
