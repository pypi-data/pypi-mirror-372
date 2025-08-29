"""Organization model."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    CodeableConcept,
    ExtendedContactDetail,
    Identifier,
    OrganizationReference,
    Qualification,
    TimeStampedModel,
)
from dfhir.endpoints.models import EndpointReference

from .choices import OrganizationStatus


class Organization(TimeStampedModel):
    """Organization model."""

    name = models.CharField(max_length=255)
    identifier = models.ManyToManyField(
        Identifier, related_name="organization_identifier", blank=True
    )
    alias = ArrayField(models.CharField(max_length=255), null=True)
    website = models.URLField(null=True)
    email = models.EmailField(null=True)
    status = models.CharField(
        max_length=50,
        choices=OrganizationStatus.choices,
        default=OrganizationStatus.PENDING,
    )
    active = models.BooleanField(default=True)
    type = models.ManyToManyField(
        CodeableConcept, related_name="organization_type", blank=True
    )
    part_of = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="organization_part_of",
    )
    description = models.TextField(null=True)
    qualification = models.ManyToManyField(
        Qualification, related_name="organization_qualification", blank=True
    )
    contact = models.ManyToManyField(
        ExtendedContactDetail, related_name="organization_contact", blank=True
    )
    endpoint = models.ManyToManyField(
        EndpointReference, related_name="organization_endpoint", blank=True
    )


class OrganizationCodeableReference(TimeStampedModel):
    """organization codeable concept model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="organization_codeable_concept_concept",
    )
    reference = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="organization_codeable_concept_reference",
    )
