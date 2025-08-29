"""charge item model choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ChargeItemStatusChoice(models.TextChoices):
    """charge item status choices."""

    PLANNED = "planned", _("Planned")
    BILLABLE = "billable", _("Billable")
    NOT_BILLABLE = "not-billable", _("Not Billable")
    ABORTED = "aborted", _("Aborted")
    BILLED = "billed", _("Billed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")
