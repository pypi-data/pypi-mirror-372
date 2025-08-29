"""medication statement model choices."""

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class MedicationStatementStatusChoices(TextChoices):
    """medication statement status choices."""

    RECORDED = "recorded", _("Recorded")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in error")
    DRAFT = "draft", _("Draft")
