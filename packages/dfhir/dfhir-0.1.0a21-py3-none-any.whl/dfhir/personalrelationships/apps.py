"""Personal Relationships App Configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PersonalrelationshipsConfig(AppConfig):
    """Personal Relationships Config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.personalrelationships"
    verbose_name = _("Personal Relationships")
