"""Endpoints models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    Availability,
    BaseReference,
    CodeableConcept,
    ContactPoint,
    Identifier,
    OrganizationReference,
    Period,
    TimeStampedModel,
)

from . import choices


class EndpointPayload(TimeStampedModel):
    """Endpoint Payload model."""

    type = models.ManyToManyField(
        CodeableConcept, related_name="endpoint_payload_type", blank=True
    )
    mime_type = ArrayField(models.CharField(max_length=255), null=True)
    # TODO: fix this
    # profile_canonical = models.CharField(max_length=255, null=True)
    profile_uri = models.CharField(max_length=255, null=True)


class Endpoint(TimeStampedModel):
    """Endpoint model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="endpoint_identifier", blank=True
    )
    status = models.CharField(
        max_length=255, choices=choices.EndpointStatusChoices.choices, null=True
    )
    connection_type = models.ManyToManyField(
        CodeableConcept, related_name="endpoint_connection_type", blank=True
    )
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    environmental_type = models.ManyToManyField(
        CodeableConcept, related_name="endpoint_environmental_type", blank=True
    )
    managing_organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        related_name="endpoint_managing_organization",
        null=True,
    )
    contact = models.ManyToManyField(
        ContactPoint, related_name="endpoint_contact", blank=True
    )
    availability = models.ForeignKey(
        Availability,
        on_delete=models.DO_NOTHING,
        related_name="endpoint_availability",
        null=True,
    )
    period = models.ForeignKey(
        Period, on_delete=models.DO_NOTHING, related_name="endpoint_period", null=True
    )
    payload = models.ManyToManyField(
        EndpointPayload, related_name="endpoint_payload", blank=True
    )
    address = models.CharField(max_length=255, null=True)
    header = ArrayField(models.CharField(max_length=255), null=True)


class EndpointReference(BaseReference):
    """Endpoint Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="endpoint_reference_identifier",
        null=True,
    )
    endpoint = models.ForeignKey(
        "Endpoint",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="endpoint_reference",
    )
