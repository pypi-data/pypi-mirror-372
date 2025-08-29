"""specimens app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SpecimensConfig(AppConfig):
    """specimens app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.specimens"
    verbose_name = _("Specimens")
