"""molecular definitions app."""

from django.apps import AppConfig


class MoleculardefinitionsConfig(AppConfig):
    """molecular definitions app config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.moleculardefinitions"
    verbose_name = "Molecular Definitions"
