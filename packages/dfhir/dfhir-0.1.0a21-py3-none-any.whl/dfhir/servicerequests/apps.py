"""service requests app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ServicerequestsConfig(AppConfig):
    """Service requests app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.servicerequests"
    verbose_name = _("Service Requests")
