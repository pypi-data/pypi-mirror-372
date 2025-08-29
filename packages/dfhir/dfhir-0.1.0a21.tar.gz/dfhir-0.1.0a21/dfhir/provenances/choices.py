"""provenance choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ProvenanceEntryRoleChoices(models.TextChoices):
    """provenance entry role choices."""

    REVISION = "revision", _("Revision")
    QUOTATION = "quotation", _("Quotation")
    SOURCE = "source", _("Source")
    INSTANTIATES = "instantiates", _("Instantiates")
    REMOVAL = "removal", _("Removal")
