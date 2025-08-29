"""RelatedPersons app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RelatedpersonsConfig(AppConfig):
    """RelatedPersons app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.relatedpersons"
    verbose_name = _("Related Persons")
