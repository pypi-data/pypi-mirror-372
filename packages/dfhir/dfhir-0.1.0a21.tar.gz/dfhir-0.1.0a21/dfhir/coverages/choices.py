"""Coverage choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class CoverageStatusChoices(models.TextChoices):
    """Coverage status choices."""

    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    DRAFT = "draft", _("Draft")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class CoverageKindChoices(models.TextChoices):
    """Coverage kind choices."""

    INSURANCE = "insurance", _("Insurance")
    SELF_PAY = "self-pay", _("Self Pay")
    OTHER = "other", _("Other")
