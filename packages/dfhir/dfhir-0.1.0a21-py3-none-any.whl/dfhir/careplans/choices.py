"""Careplan choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class CareplanStatusChoices(models.TextChoices):
    """Careplan status choices."""

    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")
    REVOKED = "revoked", _("Revoked")
    ON_HOLD = "on-hold", _("On Hold")


class CarePlanIntentChoices(models.TextChoices):
    """Careplan intent choices."""

    PROPOSAL = "proposal", _("Proposal")
    PLAN = "plan", _("Plan")
    ORDER = "order", _("Order")
    OPTION = "option", _("Option")
    DIRECTIVE = "directive", _("Directive")
