"""supply request app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SupplyrequestsConfig(AppConfig):
    """supply request app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.supplyrequests"
    verbose_name = _("Supply request")
