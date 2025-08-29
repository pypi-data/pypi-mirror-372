"""Family member history app config."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FamilymemberhistoriesConfig(AppConfig):
    """Family member history app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.familymemberhistories"
    verbose_name = _("Family Member Histories")
