"""Flag app config."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FlagsConfig(AppConfig):
    """Flag app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.flags"
    verbose_name = _("Flags")
