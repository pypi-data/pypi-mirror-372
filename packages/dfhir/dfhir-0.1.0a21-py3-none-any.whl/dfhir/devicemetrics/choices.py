"""Device choices."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DeviceMetricOperationalStatus(models.TextChoices):
    """Device metric operational status choices."""

    ON = "on", _("on")
    OFF = "off", _("off")
    STANDBY = "standby", _("standby")
    ENTERED_IN_ERROR = "entered-in-error", _("Entered in Error")


class DeviceMetricCalibrationState(models.TextChoices):
    """Device metric calibration state choices."""

    NOT_CALIBRATED = "not-calibrated", _("Not Calibrated")
    CALIBRATION_REQUIRED = "calibration-required", _("Calibration Required")
    CALIBRATED = "calibrated", _("Calibrated")
    UNSPECIFIED = "unspecified", _("Unspecified")
