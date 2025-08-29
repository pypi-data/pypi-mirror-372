"""immunization model choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ImmunizationStatusChoices(models.TextChoices):
    """immunization status choices."""

    COMPLETED = "completed", _("Completed")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    NOT_DONE = "not-done", _("Not Done")
