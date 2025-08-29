"""activity definition app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ActivitydefinitionsConfig(AppConfig):
    """activity definition app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.activitydefinitions"
    verbose_name = _("Activity Definitions")
