"""payment reconciliations model choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentReconciliationStatusChoices(models.TextChoices):
    """Payment Reconciliation status choices."""

    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    DRAFT = "draft", _("Draft")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class PaymentReconciliationOutcomeChoices(models.TextChoices):
    """Payment Reconciliation outcome choices."""

    QUEUED = "queued", _("Queued")
    COMPLETE = "complete", _("Complete")
    ERROR = "error", _("Error")
    PARTIAL = "partial", _("Partial")


class PaymentReconciliationProcessNoteChoices(models.TextChoices):
    """Payment Reconciliation Process Note choices."""

    DISPLAY = "display", _("Display")
    PRINT = "print", _("Print")
    PRINTOPER = "printoper", _("Print Oper")
