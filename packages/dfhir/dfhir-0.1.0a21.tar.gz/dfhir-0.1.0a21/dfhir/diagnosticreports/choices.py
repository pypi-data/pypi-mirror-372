"""diagnostic report choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class SupportingInfoChoices(TextChoices):
    """Supporting info choices."""

    QUESTION = "question", _("Question")
    RESULT = "result", _("Result")
    SUPPORTING_CLINICAL_INFORMATION = (
        "supporting_clinical_information",
        _("Supporting Clinical Information"),
    )


class DiagnosticReportStatus(TextChoices):
    """diagnostic report status choices."""

    REGISTERED = "registered", _("Registered")
    PARTIAL = "partial", _("Partial")
    PRELIMINARY = "preliminary", _("Preliminary")
    MODIFIED = "modified", _("Modified")
    FINAL = "final", _("Final")
    AMENDED = "amended", _("Amended")
    CORRECTED = "corrected", _("Corrected")
    APPENDED = "appended", _("Appended")
    CANCELLED = "cancelled", _("Cancelled")
    ENTERED_IN_ERROR = "entered_in_error", _("Entered in Error")
