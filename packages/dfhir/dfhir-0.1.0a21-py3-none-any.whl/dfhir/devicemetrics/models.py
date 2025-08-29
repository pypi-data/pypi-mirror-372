"""Device metrics models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Quantity,
    TimeStampedModel,
)

from . import choices


class DeviceMetricCalibration(TimeStampedModel):
    """Device Metric Calibration model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="device_metric_calibration_type",
        null=True,
    )
    state = models.CharField(
        max_length=255, choices=choices.DeviceMetricCalibrationState.choices, null=True
    )
    time = models.DateTimeField(null=True)


class DeviceMetric(TimeStampedModel):
    """Device Metric model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="device_metrics_identifier", blank=True
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="device_metric_type",
        null=True,
    )
    unit = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="device_metric_unit",
        null=True,
    )
    device = models.ForeignKey(
        "devices.DeviceReference",
        on_delete=models.DO_NOTHING,
        related_name="device_metric_device",
        null=True,
    )
    operational_status = models.CharField(
        max_length=255, choices=choices.DeviceMetricOperationalStatus.choices, null=True
    )
    color = models.CharField(max_length=255, null=True)
    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="device_metric_category",
    )
    measurement_frequency = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="device_metric_measurement_frequency",
        null=True,
    )
    calibration = models.ManyToManyField(
        DeviceMetricCalibration, related_name="device_metric_calibration", blank=True
    )


class DeviceMetricReference(BaseReference):
    """Device Metric Reference model."""

    device_metric = models.ForeignKey(
        DeviceMetric,
        on_delete=models.DO_NOTHING,
        related_name="device_metric_reference",
        null=True,
    )
    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="device_metric_reference_identifier",
        null=True,
    )
