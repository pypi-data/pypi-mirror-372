"""molecular sequences app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MolecularsequencesConfig(AppConfig):
    """molecular sequences config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.molecularsequences"
    verbose_name = _("Molecular Sequences")
