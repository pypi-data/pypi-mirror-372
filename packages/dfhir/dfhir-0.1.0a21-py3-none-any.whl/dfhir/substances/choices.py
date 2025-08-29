"""Substances Choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class SubstanceStatusChoices(models.TextChoices):
    """Substance Status Choices."""

    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
