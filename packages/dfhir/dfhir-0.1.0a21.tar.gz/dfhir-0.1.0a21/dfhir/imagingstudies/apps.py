"""imaging study app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ImagingstudyConfig(AppConfig):
    """imaging study app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.imagingstudies"
    verbose_name = _("Imaging Study")
