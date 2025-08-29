"""biologically derived product dispenses choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class BiologicallyDerivedProductDispenseStatus(models.TextChoices):
    """Biologically derived product dispense status choices."""

    PREPARATION = "preparation", _("Preparation")
    IN_PERSON = "in-person", _("In Person")
    ALLOCATED = "allocated", _("Allocated")
    ISSUED = "issued", _("Issued")
    UNFULFILLED = "unfulfilled", _("Unfulfilled")
    RETURNED = "returned", _("Returned")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")
