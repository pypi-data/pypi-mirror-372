"""organization affiliations app."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class OrganizationaffiliationsConfig(AppConfig):
    """Organization affiliations configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.organizationaffiliations"
    verbose_name = _("Organization Affiliations")
