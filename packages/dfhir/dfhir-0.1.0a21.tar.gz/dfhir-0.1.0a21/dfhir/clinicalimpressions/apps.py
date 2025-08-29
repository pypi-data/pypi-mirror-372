"""Clinical impressions app config."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ClinicalimpressionsConfig(AppConfig):
    """Clinical impressions app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.clinicalimpressions"
    verbose_name = _("Clinical Impressions")
