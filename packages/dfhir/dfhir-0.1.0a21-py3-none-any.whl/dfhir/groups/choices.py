"""Group choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class GroupStatus(models.TextChoices):
    """Group status choices."""

    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    RETIRED = "retired", _("Retired")
    UNKNOWN = "unknown", _("Unknown")


class GroupMembershipChoices(models.TextChoices):
    """Group membership choices."""

    DEFINITIONAL = "definitional", _("Definitional")
    CONCEPTUAL = "conceptual", _("Conceptual")
    ENUMERATED = "enumerated", _("Enumerated")


class GroupCombinationMethodChoices(models.TextChoices):
    """Group combination method choices."""

    ALL_OF = "all-of", _("All Of")
    ANY_OF = "any-of", _("Any Of")
    AT_LEAST = "at-least", _("At Least")
    AT_MOST = "at-most", _("At Most")
    EXCEPT_SUBSET = "except-subset", _("Except Subset")


class GroupTypeChoices(models.TextChoices):
    """Group types choices."""

    PERSON = "person", _("Person")
    ANIMAL = "animal", _("Animal")
    PRACTITIONER = "practitioner", _("Practitioner")
    DEVICE = "device", _("Device")
    CARE_TEAM = "care-team", _("Care Team")
    HEALTHCARE_SERVICE = "healthcare-service", _("Healthcare Service")
    LOCATION = "location", _("Location")
    ORGANIZATION = "organization", _("Organization")
