"""Nutrition Products Choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class NutritionProductStatusChoices(TextChoices):
    """Nutrition Product Status Choices."""

    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
