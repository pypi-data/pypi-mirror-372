"""Invoice choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class InvoiceStatus(models.TextChoices):
    """Invoice status choices."""

    DRAFT = "draft", _("Draft")
    ISSUED = "issued", _("Issued")
    BALANCED = "balanced", _("Balanced")
    CANCELLED = "cancelled", _("Cancelled")
    ENTERED_IN_ERROR = "entered_in_error", _("Entered in error")
