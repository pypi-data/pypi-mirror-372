"""risk assessment model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class RiskAssessmentStatusChoices(TextChoices):
    """risk assessment status choices."""

    REGISTERED = "registered", _("Registered")
    SPECIMEN_IN_PROGRESS = "specimen-in-progress", _("Specimen in Progress")
    PRELIMINARY = "preliminary", _("Preliminary")
    FINAL = "final", _("Final")
    AMENDED = "amended", _("Amended")
    CORRECTED = "corrected", _("Corrected")
    APPENDED = "appended", _("Appended")
    CANCELLED = "cancelled", _("Cancelled")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    UNKNOWN = "unknown", _("Unknown")
    CANNOT_BE_OBTAINED = "cannot-be-obtained", _("Con not be Obtained")
