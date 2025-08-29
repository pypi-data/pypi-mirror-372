"""transport app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TransportsConfig(AppConfig):
    """Transport app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.transports"
    verbose_name = _("Transports")
