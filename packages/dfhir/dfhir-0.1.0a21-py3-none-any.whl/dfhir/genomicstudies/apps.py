"""genomic study app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GenomicstudyConfig(AppConfig):
    """Genomic study app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.genomicstudies"
    verbose_name = _("Genomic Study")
