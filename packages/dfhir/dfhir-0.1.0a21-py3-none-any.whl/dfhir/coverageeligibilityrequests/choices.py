"""CoverageEligibilityRequest choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class CoverageEligibilityRequestStatus(models.TextChoices):
    """CoverageEligibilityRequestStatus choices."""

    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    DRAFT = "draft", _("Draft")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class CoverageEligibilityRequestPurpose(models.TextChoices):
    """CoverageEligibilityRequestPurpose choices."""

    AUTH_REQUIREMENTS = "auth-requirements", _("Auth Requirements")
    BENEFITS = "benefits", _("Benefits")
    DISCOVERY = "discovery", _("Discovery")
    VALIDATION = "validation", _("Validation")
