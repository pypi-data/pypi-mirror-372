"""immunization evaluations model choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ImmunizationEvaluationStatusChoices(models.TextChoices):
    """Immunization Evaluation status choices."""

    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
