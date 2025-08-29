"""document reference model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class DocumentReferenceStatusChoices(TextChoices):
    """document reference status choices."""

    CURRENT = "current", _("Current")
    SUPPRESSED = "suppressed", _("Suppressed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in error")


class DocumentReferenceDocStatusChoices(TextChoices):
    """document reference doc status choices."""

    REGISTERED = "registered", _("Registered")
    PARTIAL = "partial", _("Partial")
    PRELIMINARY = "preliminary", _("Preliminary")
    FINAL = "final", _("Final")
    AMENDED = "amended", _("Amended")
    CORRECTED = "corrected", _("Corrected")
    APPENDED = "appended", _("Appended")
    CANCELLED = "cancelled", _("Cancelled")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in error")
    DEPRECATED = "deprecated", _("Deprecated")
    UNKNOWN = "unknown", _("Unknown")
