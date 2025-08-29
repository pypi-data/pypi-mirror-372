"""Claims choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ClaimStatus(models.TextChoices):
    """Claim status choices."""

    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    DRAFT = "draft", _("Draft")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class ClaimUseChoices(models.TextChoices):
    """Claim use choices."""

    CLAIM = "claim", _("Claim")
    PREAUTHORIZATION = "preauthorization", _("Preauthorization")
    PREDETERMINATION = "predetermination", _("Predetermination")
