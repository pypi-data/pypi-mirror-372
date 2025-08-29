"""Payment Notices choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class PaymentNoticeStatus(models.TextChoices):
    """Payment Notice Status choices."""

    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    DRAFT = "draft", _("Draft")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
