"""Account choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AccountStatus(models.TextChoices):
    """Account status choices."""

    ACTIVE = "active", _("Active")
    INACTIVE = "inactive", _("Inactive")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    ON_HOLD = "on-hold", _("On Hold")
    UNKNOWN = "unknown", _("Unknown")
