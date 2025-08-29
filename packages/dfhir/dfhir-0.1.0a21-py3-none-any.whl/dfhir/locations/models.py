"""Location models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    Address,
    Availability,
    BaseReference,
    CodeableConcept,
    Coding,
    ExtendedContactDetail,
    Identifier,
    OrganizationReference,
    TimeStampedModel,
    VirtualServiceDetails,
)
from dfhir.endpoints.models import EndpointReference

from .choices import (
    LocationMode,
    LocationStatus,
)


class Position(TimeStampedModel):
    """Position model."""

    longitude = models.FloatField()
    latitude = models.FloatField()
    altitude = models.FloatField(null=True)

    def __str__(self):
        """Return position as string representation."""
        return f"{self.longitude}, {self.latitude}"


class LocationReference(BaseReference):
    """Location Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="location_reference_identifier",
    )
    location = models.ForeignKey(
        "Location",
        on_delete=models.DO_NOTHING,
        related_name="location_reference",
        null=True,
    )


class LocationOrganizationReference(BaseReference):
    """Location Organization Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="location_organization_reference_identifier",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="location_organization_reference",
        null=True,
    )
    location = models.ForeignKey(
        "Location",
        on_delete=models.DO_NOTHING,
        related_name="location_organization_reference",
        null=True,
    )


class Location(TimeStampedModel):
    """Location model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="location_identifier", blank=True
    )
    name = models.CharField(max_length=255)
    status = models.CharField(
        choices=LocationStatus.choices, max_length=255, default=LocationStatus.ACTIVE
    )
    operational_status = models.ForeignKey(
        Coding,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="location_operational_status",
    )
    alias = ArrayField(models.CharField(max_length=255), null=True)
    description = models.TextField(null=True)
    mode = models.CharField(choices=LocationMode.choices, max_length=255, null=True)
    address = models.ForeignKey(Address, on_delete=models.DO_NOTHING, null=True)
    form = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="location_form",
    )
    position = models.ForeignKey(Position, on_delete=models.DO_NOTHING, null=True)
    managing_organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        related_name="location_organization",
        null=True,
    )
    part_of = models.ForeignKey(
        LocationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="location_part_of",
    )
    hours_of_operation = models.ForeignKey(
        Availability, on_delete=models.DO_NOTHING, null=True
    )
    type = models.ManyToManyField(
        CodeableConcept, related_name="location_type", blank=True
    )
    characteristic = models.ManyToManyField(
        CodeableConcept, related_name="location_characteristic", blank=True
    )
    contact = models.ManyToManyField(
        ExtendedContactDetail, related_name="location_contact", blank=True
    )
    endpoint = models.ManyToManyField(
        EndpointReference, related_name="location_endpoint", blank=True
    )
    virtual_service_details = models.ManyToManyField(
        VirtualServiceDetails,
        related_name="location_virtual_service_details",
        blank=True,
    )

    def __str__(self):
        """Return name as string representation."""
        return self.name


class LocationCodeableReference(TimeStampedModel):
    """Location Codeable Reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="location_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        LocationReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="location_codeable_reference_reference",
    )
