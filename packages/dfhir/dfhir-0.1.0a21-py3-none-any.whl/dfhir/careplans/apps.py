"""care plan app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CareplansConfig(AppConfig):
    """Care Plans Config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.careplans"
    verbose_name = _("Care Plans")
