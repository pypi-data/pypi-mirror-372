"""CoverageEligibilityResponse status choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class CoverageEligibilityResponseStatus(models.TextChoices):
    """CoverageEligibilityResponse status code choices."""

    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    DRAFT = "draft", _("Draft")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class CoverageEligibilityResponsePurpose(models.TextChoices):
    """CoverageEligibilityResponse purpose code choices."""

    AUTH_REQUIREMENTS = "auth-requirements", _("Auth Requirements")
    BENEFITS = "benefits", _("Benefits")
    DISCOVERY = "discovery", _("Discovery")
    VALIDATION = "validation", _("Validation")


class CoverageEligibilityResponseOutcome(models.TextChoices):
    """CoverageEligibilityResponse outcome code choices."""

    QUEUED = "queued", _("Queued")
    COMPLETE = "complete", _("Complete")
    ERROR = "error", _("Error")
    PARTIAL = "partial", _("Partial")
