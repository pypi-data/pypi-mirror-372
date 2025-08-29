"""Claims app config."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClaimsConfig(AppConfig):
    """Claims app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.claims"
    verbose_name = _("Claims")
