"""Choices for the persons app."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class LinkAssuranceChoices(models.TextChoices):
    """Link Assurance Choices."""

    LEVEL1 = "level1", _("level1")
    LEVEL2 = "level2", _("level2")
    LEVEL3 = "level3", _("level3")
    LEVEL4 = "level4", _("level4")
