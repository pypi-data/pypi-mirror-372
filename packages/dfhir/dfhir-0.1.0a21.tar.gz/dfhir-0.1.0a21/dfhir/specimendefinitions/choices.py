"""Specimen definition choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class SpecimenDefinitionStatusChoices(models.TextChoices):
    """Specimen definition status choices."""

    DRAFT = "draft", _("draft")
    ACTIVE = "active", _("active")
    RETIRED = "retired", _("retired")
    UNKNOWN = "unknown", _("unknown")


class SpecimenDefinitionTestedTypePreferenceChoices(models.TextChoices):
    """Specimen definition tested type preference choices."""

    PREFERRED = "preferred", _("preferred")
    ALTERNATE = "alternate", _("alternate")
