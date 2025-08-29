"""Goals app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GoalsConfig(AppConfig):
    """Goals app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.goals"
    verbose_name = _("Goals")
