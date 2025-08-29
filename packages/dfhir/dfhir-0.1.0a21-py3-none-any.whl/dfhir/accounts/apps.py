"""Accounts app configuration."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    """Accounts config."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "dfhir.accounts"
    verbose_name = _("Accounts")
