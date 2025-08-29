"""nutrition order model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class NutritionOrderStatusChoices(TextChoices):
    """nutrition order status choices."""

    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    ON_HOLD = "on-hold", _("On Hold")
    REVOKED = "revoked", _("Revoked")
    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")


class NutritionOrderIntentChoices(TextChoices):
    """nutrition order intent choices."""

    PROPOSAL = "proposal", _("Proposal")
    PLAN = "plan", _("Plan")
    ORDER = "order", _("Order")
    DIRECTIVE_ORDER = "directive-order", _("Directive Order")
    ORIGINAL_ORDER = "original-order", _("Original Order")
    REFLEX_ORDER = "reflex-order", _("Reflex Order")
    FILLER_ORDER = "filler-order", _("Filler Order")
    INSTANCE_ORDER = "instance-order", _("Instance Order")
    OPTION = "option", _("Option")


class NutritionOrderPriorityChoices(TextChoices):
    """nutrition order priority choices."""

    ROUTINE = "routine", _("Routine")
    URGENT = "urgent", _("Urgent")
    STAT = "stat", _("Stat")
    ASAP = "asap", _("ASAP")
