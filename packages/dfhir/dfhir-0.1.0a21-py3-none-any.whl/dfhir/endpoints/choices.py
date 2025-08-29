"""Endpoint choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class EndpointStatusChoices(models.TextChoices):
    """Endpoint status choices."""

    ACTIVE = "active", _("active")
    LIMITED = "limited", _("limited")
    SUSPENDED = "suspended", _("suspended")
    ERROR = "error", _("error")
    OFF = "off", _("off")
    ENTERED_IN_ERROR = "entered-in-error", _("entered-in-error")


class EndpointEnvironmentChoices(models.TextChoices):
    """Endpoint environment choices."""

    DEVELOPMENT = "development", _("development")
    TEST = "test", _("test")
    PRODUCTION = "production", _("production")
    STAGING = "staging", _("staging")
    TRAINING = "training", _("training")
