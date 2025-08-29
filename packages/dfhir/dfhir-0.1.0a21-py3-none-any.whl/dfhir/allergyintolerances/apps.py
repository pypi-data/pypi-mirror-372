"""Allergy intolerances app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AllergyintolerancesConfig(AppConfig):
    """Allergy intolerances app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.allergyintolerances"
    verbose_name = _("Allergy Intolerances")
