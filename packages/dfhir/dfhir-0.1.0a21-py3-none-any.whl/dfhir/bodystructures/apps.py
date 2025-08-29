"""body structure app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BodystructuresConfig(AppConfig):
    """body structure app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.bodystructures"
    verbose_name = _("Body Structures")
