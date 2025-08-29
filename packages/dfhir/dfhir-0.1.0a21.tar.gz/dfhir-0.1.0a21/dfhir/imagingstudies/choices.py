"""imaging study model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class ImagingStudyStatusChoices(TextChoices):
    """Imaging study status choices."""

    REGISTERED = "registered", _("Registered")
    AVAILABLE = "available", _("Available")
    CANCELLED = "cancelled", _("Cancelled")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in error")
    UNKNOWN = "unknown", _("Unknown")
    INACTIVE = "inactive", _("Inactive")
