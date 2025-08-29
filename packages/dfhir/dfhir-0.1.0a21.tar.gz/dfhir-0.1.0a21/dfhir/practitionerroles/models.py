"""Practitioner Role models."""

from django.db import models

from dfhir.base.models import (
    Availability,
    BaseReference,
    CodeableConcept,
    ExtendedContactDetail,
    Identifier,
    OrganizationReference,
    Period,
    TimeStampedModel,
)
from dfhir.endpoints.models import EndpointReference
from dfhir.healthcareservices.models import HealthCareServiceReference
from dfhir.locations.models import LocationReference


class PractitionerRoleCode(TimeStampedModel):
    """Practitioner Role Code model."""

    display = models.CharField(max_length=255)
    definition = models.TextField(null=True)


class PractitionerRole(TimeStampedModel):
    """Practitioner Role model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="practitioner_role_identifier", blank=True
    )
    active = models.BooleanField(default=True)
    period = models.ForeignKey(
        Period, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    practitioner = models.ForeignKey(
        "practitioners.PractitionerReference",
        on_delete=models.CASCADE,
        related_name="practitioner_role_practitioner",
    )
    organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="practitioner_role_organization",
    )
    network = models.ManyToManyField(
        OrganizationReference, related_name="practitioner_role_network", blank=True
    )
    code = models.ManyToManyField(
        CodeableConcept, related_name="practitioner_role_code", blank=True
    )
    display = models.TextField(null=True)
    specialty = models.ManyToManyField(
        CodeableConcept, related_name="practitioner_role_specialty", blank=True
    )
    location = models.ManyToManyField(
        LocationReference, related_name="practitioner_role_location", blank=True
    )
    healthcare_service = models.ManyToManyField(
        HealthCareServiceReference, related_name="practitioner_role_healthcareservice"
    )
    contact = models.ManyToManyField(
        ExtendedContactDetail, related_name="practitioner_role_contact", blank=True
    )
    characteristic = models.ManyToManyField(
        CodeableConcept, related_name="practitioner_role_characteristic", blank=True
    )
    communication = models.ManyToManyField(
        CodeableConcept, related_name="practitioner_role_communication", blank=True
    )
    availability = models.ForeignKey(
        Availability,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="practitioner_role_availability",
    )
    endpoint = models.ManyToManyField(
        EndpointReference, related_name="practitioner_role_endpoint", blank=True
    )


class PractitionerRoleReference(BaseReference):
    """Practitioner Role Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="practitioner_role_reference_identifier",
    )
    practitioner_role = models.ForeignKey(
        PractitionerRole,
        on_delete=models.CASCADE,
        related_name="practitioner_role_reference_practitioner_role",
    )
