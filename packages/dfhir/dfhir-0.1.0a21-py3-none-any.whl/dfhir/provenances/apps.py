"""provenances app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProvenancesConfig(AppConfig):
    """Provenances app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.provenances"
    verbose_name = _("Provenances")
