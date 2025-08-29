"""observation definitions app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ObservationdefinitionsConfig(AppConfig):
    """observation definitions app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.observationdefinitions"
    verbose_name = _("Observation Definitions")
