"""document reference app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DocumentreferencesConfig(AppConfig):
    """Document references app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.documentreferences"
    verbose_name = _("Document References")
