"""Groups app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GroupsConfig(AppConfig):
    """Groups config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.groups"
    verbose_name = _("Groups")
