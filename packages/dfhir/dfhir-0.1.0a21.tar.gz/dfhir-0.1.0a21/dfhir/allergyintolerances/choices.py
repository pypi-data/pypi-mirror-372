"""Allergy intolerance choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AllergyIntoleranceCategory(models.TextChoices):
    """Allergy Intolerance category choices."""

    FOOD = "food", _("Food")
    MEDICATION = "medication", _("Medication")
    ENVIRONMENT = "environment", _("Environment")
    BIOLOGIC = "biologic", _("Biologic")


class AllergyIntoleranceCriticality(models.TextChoices):
    """Allergy Intolerance criticality choices."""

    LOW = "low", _("Low")
    HIGH = "high", _("High")
    UNABLE_TO_ASSESS = "unable-to-assess", _("Unable to Assess")


class AllergyIntoleranceSeverity(models.TextChoices):
    """Allergy Intolerance severity choices."""

    MILD = "mild", _("Mild")
    MODERATE = "moderate", _("Moderate")
    SEVERE = "severe", _("Severe")
