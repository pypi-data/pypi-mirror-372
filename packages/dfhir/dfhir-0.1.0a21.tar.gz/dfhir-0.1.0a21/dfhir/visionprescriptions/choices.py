"""Vision prescription choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class VisionPrescriptionStatusChoices(models.TextChoices):
    """Vision prescription status choices."""

    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    DRAFT = "draft", _("Draft")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class VisionPrescriptionLensSpecificationEyeChoices(models.TextChoices):
    """Vision prescription lens specification eye choices."""

    RIGHT = "right", _("Right")
    LEFT = "left", _("Left")


class VisionPrescriptionLensSpecificationPrismBaseChoices(models.TextChoices):
    """Vision prescription lens specification prism base choices."""

    UP = "up", _("Up")
    DOWN = "down", _("Down")
    IN = "in", _("In")
    OUT = "out", _("Out")
