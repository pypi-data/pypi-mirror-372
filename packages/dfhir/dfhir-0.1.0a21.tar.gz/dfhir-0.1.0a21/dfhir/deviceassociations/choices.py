"""Deviceassociations choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceAssociationStatus(models.TextChoices):
    """DeviceAssociationStatus choices."""

    IMPLANTED = "implanted", _("Implanted")
    EXPLANTED = "explanted", _("Explanted")
    ATTACHED = "attached", _("Attached")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")
