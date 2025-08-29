"""organization affiliation models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    ExtendedContactDetail,
    Identifier,
    Period,
    TimeStampedModel,
)


class OrganizationAffiliation(TimeStampedModel):
    """organization affiliation model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="organization_affiliations", blank=True
    )
    active = models.BooleanField(default=True)
    period = models.ForeignKey(
        Period,
        on_delete=models.SET_NULL,
        null=True,
        related_name="organization_affiliations_period",
    )
    organization = models.ForeignKey(
        "base.OrganizationReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="organization_affiliations",
    )
    participating_organization = models.ForeignKey(
        "base.OrganizationReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="participating_organization_affiliations",
    )
    network = models.ManyToManyField(
        "base.OrganizationReference",
        blank=True,
        related_name="network_organization_affiliations",
    )
    code = models.ManyToManyField(
        "base.CodeableConcept", blank=True, related_name="organization_affiliation_code"
    )
    specialty = models.ManyToManyField(
        "base.CodeableConcept",
        blank=True,
        related_name="organization_affiliation_specialty",
    )
    location = models.ManyToManyField(
        "locations.LocationReference",
        blank=True,
        related_name="organization_affiliation_location",
    )
    healthcare_service = models.ManyToManyField(
        "healthcareservices.HealthcareServiceReference",
        blank=True,
        related_name="organization_affiliation_healthcare_service",
    )
    contact = models.ManyToManyField(
        ExtendedContactDetail,
        blank=True,
        related_name="organization_affiliation_contact",
    )
    endpoint = models.ManyToManyField(
        "endpoints.EndpointReference",
        blank=True,
        related_name="organization_affiliation_endpoint",
    )


class OrganizationAffiliationReference(BaseReference):
    """organization affiliation reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="organization_affiliation_references_identifier",
    )
    organization_affiliation = models.ForeignKey(
        OrganizationAffiliation,
        on_delete=models.CASCADE,
        related_name="organization_affiliation_references_organization_affiliation",
    )
