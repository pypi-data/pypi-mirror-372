"""Device models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    Attachment,
    BaseReference,
    CodeableConcept,
    ContactPoint,
    Identifier,
    OrganizationReference,
    Quantity,
    Range,
    TimeStampedModel,
)

from . import choices


class DeviceUdiCarrier(TimeStampedModel):
    """Device UDI carrier model."""

    device_identifier = models.CharField(max_length=255, null=True)
    device_identifier_system = models.CharField(max_length=255, null=True)
    carrier_hrft = models.CharField(max_length=255, null=True)
    carrier_aidc = models.CharField(max_length=255, null=True)
    issuer = models.CharField(max_length=255, null=True)
    jurisdiction = models.CharField(max_length=255, null=True)
    carrier = models.CharField(max_length=255, null=True)
    entry_type = models.CharField(max_length=255, null=True)


class DeviceName(TimeStampedModel):
    """Device name model."""

    value = models.CharField(max_length=255, null=True)
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_name_type",
    )
    display = models.BooleanField(null=True, default=False)


class DeviceVersion(TimeStampedModel):
    """Device version model."""

    value = models.CharField(max_length=255, null=True)
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_version_type",
    )
    component = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_version_component",
    )
    install_date = models.DateTimeField(null=True)


class DeviceConformsTo(TimeStampedModel):
    """Device conforms to model."""

    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_conforms_to_category",
    )
    specification = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_conforms_to_specification",
    )
    version = models.CharField(max_length=255, null=True)


class DeviceProperty(TimeStampedModel):
    """Device property model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_property_type",
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        related_name="device_property_value_code",
        on_delete=models.CASCADE,
        null=True,
    )
    value_string = models.CharField(max_length=255, null=True)
    value_boolean = models.BooleanField(null=True)
    value_integer = models.IntegerField(null=True)
    value_quantity = models.ForeignKey(
        Quantity,
        related_name="device_property_value_quantity",
        on_delete=models.CASCADE,
        null=True,
    )
    value_range = models.ForeignKey(
        Range,
        related_name="device_property_value_range",
        on_delete=models.CASCADE,
        null=True,
    )
    value_attachment = models.ForeignKey(
        Attachment,
        related_name="device_property_value_attachment",
        on_delete=models.CASCADE,
        null=True,
    )


class Device(TimeStampedModel):
    """Device model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="devices_identifier", blank=True
    )
    definition = models.ForeignKey(
        "devicedefinitions.DeviceDefinitionReference",
        on_delete=models.CASCADE,
        null=True,
    )
    status = models.CharField(
        max_length=255, choices=choices.DeviceStatus.choices, null=True
    )
    udi_carrier = models.ManyToManyField(DeviceUdiCarrier, blank=True)
    availability_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="devices_availability_status",
        null=True,
    )
    biological_source_event = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        null=True,
        related_name="devices_biological_source_event",
    )
    manufacturer = models.CharField(max_length=255, null=True)
    manufacture_date = models.DateTimeField(null=True)
    expiration_date = models.DateTimeField(null=True)
    lot_number = models.CharField(max_length=255, null=True)
    serial_number = models.CharField(max_length=255, null=True)
    name = models.ManyToManyField(DeviceName, related_name="devices_name", blank=True)
    model_number = models.CharField(max_length=255, null=True)
    part_number = models.CharField(max_length=255, null=True)
    category = models.ManyToManyField(
        CodeableConcept, related_name="devices_category", blank=True
    )
    type = models.ManyToManyField(
        CodeableConcept, related_name="devices_type", blank=True
    )
    device_version = models.ManyToManyField(
        DeviceVersion, related_name="devices_device_version", blank=True
    )
    conforms_to = models.ManyToManyField(
        DeviceConformsTo, related_name="devices_conforms_to", blank=True
    )
    property = models.ManyToManyField(
        DeviceProperty, related_name="devices_property", blank=True
    )
    mode = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="devices_mode",
        null=True,
    )
    cycle = models.IntegerField(null=True)
    duration = models.ForeignKey(
        Quantity, on_delete=models.CASCADE, related_name="devices_duration", null=True
    )
    owner = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="devices_owner",
        null=True,
    )
    contact = models.ManyToManyField(
        ContactPoint, related_name="devices_contact", blank=True
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.CASCADE,
        related_name="devices_location",
        null=True,
    )
    url = models.URLField(null=True)
    endpoint = models.ForeignKey(
        "endpoints.EndpointReference",
        on_delete=models.CASCADE,
        related_name="devices_endpoint",
        null=True,
    )
    gateway = models.ManyToManyField(
        "DeviceCodeableReference", related_name="devices_gateway", blank=True
    )
    note = models.ManyToManyField(Annotation, related_name="devices_note", blank=True)
    safety = models.ManyToManyField(
        CodeableConcept, related_name="devices_safety", blank=True
    )
    parent = models.ForeignKey(
        "DeviceReference",
        on_delete=models.CASCADE,
        related_name="devices_parent",
        null=True,
    )


class DeviceReference(BaseReference):
    """Device reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        null=True,
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        null=True,
    )


class DeviceCodeableReference(TimeStampedModel):
    """device codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        DeviceReference,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_codeable_reference_reference",
    )
    identifier = models.ForeignKey(
        Identifier,
        related_name="device_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    device = models.ForeignKey(
        Device,
        related_name="device_reference_device",
        on_delete=models.CASCADE,
        null=True,
    )


class DeviceDeviceMetricReference(BaseReference):
    """device device metric reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="device_device_metric_reference_identifier",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        related_name="device_device_metric_reference_device",
    )
    device_metric = models.ForeignKey(
        "devicemetrics.DeviceMetric",
        on_delete=models.SET_NULL,
        null=True,
        related_name="device_device_metric_reference_device_metric",
    )


class DeviceDeviceDefinitionReference(BaseReference):
    """device device definition reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="device_device_definition_reference_identifier",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        related_name="device_device_definition_reference_device",
    )
    device_definition = models.ForeignKey(
        "devicedefinitions.DeviceDefinition",
        on_delete=models.SET_NULL,
        null=True,
        related_name="device_device_definition_reference_device_definition",
    )


class DeviceDeviceDefinitionCodeableReference(TimeStampedModel):
    """device device definition codeable reference model."""

    reference = models.ForeignKey(
        DeviceDeviceDefinitionReference,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_device_definition_codeable_reference_reference",
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_device_definition_codeable_reference_concept",
    )
