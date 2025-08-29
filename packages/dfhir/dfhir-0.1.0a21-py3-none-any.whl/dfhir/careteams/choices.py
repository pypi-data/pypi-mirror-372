"""Care Team choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class CareTeamStatusChoices(models.TextChoices):
    """Care Team status choices."""

    PROPOSED = "proposed", _("Proposed")
    ACTIVE = "active", _("Active")
    SUSPENDED = "suspended", _("Suspended")
    INACTIVE = "inactive", _("Inactive")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
