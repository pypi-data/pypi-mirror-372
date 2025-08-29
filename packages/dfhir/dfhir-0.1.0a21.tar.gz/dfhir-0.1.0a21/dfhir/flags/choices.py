"""Choices for the Flag app."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class FlagStatusChoices(models.TextChoices):
    """Flag status choices."""

    ACTIVE = "active", _("active")
    INACTIVE = "inactive", _("inactive")
    ENTERED_IN_ERROR = "entered-in-error", _("entered-in-error")
