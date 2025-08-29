"""medication knowledge choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class MedicationKnowledgeStatusChoices(TextChoices):
    """Medication knowledge status choices."""

    DRAFT = "draft", _("Draft")
    ACTIVE = "active", _("Active")
    RETIRED = "retired", _("Retired")
    UNKNOWN = "unknown", _("Unknown")
