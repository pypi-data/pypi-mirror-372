"""inventory report choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class InventoryReportStatusChoices(models.TextChoices):
    """inventory report status choices."""

    DRAFT = "draft", _("Draft")
    REQUESTED = "requested", _("Requested")
    ACTIVE = "active", _("Active")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered In Error")


class InventoryReportCountTypeChoices(models.TextChoices):
    """inventory report count type choices."""

    SNAPSHOT = "snapshot", _("Snapshot")
    DIFFERENCE = "difference", _("Difference")
