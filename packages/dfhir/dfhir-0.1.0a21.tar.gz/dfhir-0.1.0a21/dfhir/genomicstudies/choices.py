"""genomic study choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class GenomicStudyStatusChoices(TextChoices):
    """genomic study status choices."""

    REGISTERED = "registered", _("Registered")
    AVAILABLE = "available", _("Available")
    CANCELLED = "cancelled", _("Cancelled")
    ENTER_IN_ERROR = "enter-in-error", _("Enter in Error")
    UNKNOWN = "unknown", _("Unknown")
