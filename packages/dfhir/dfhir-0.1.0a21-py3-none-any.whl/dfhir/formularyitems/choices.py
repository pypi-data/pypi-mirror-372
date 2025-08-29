"""formulary item model choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class FormularyItemStatusChoices(models.TextChoices):
    """Formulary item status choices."""

    ACTIVE = "active", _("Active")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")
    INACTIVE = "inactive", _("Inactive")
