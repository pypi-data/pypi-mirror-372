"""Personal Relationships models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    OrganizationReference,
    Period,
    TimeStampedModel,
)


class PersonalRelationshipSourceReference(BaseReference):
    """Personal Relationship Source Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="personal_relationship_source_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        related_name="personal_relationship_source_reference_patient",
        on_delete=models.CASCADE,
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        related_name="personal_relationship_source_reference_related_person",
        on_delete=models.CASCADE,
        null=True,
    )
    person = models.ForeignKey(
        "persons.Person",
        related_name="personal_relationship_source_reference_person",
        on_delete=models.CASCADE,
        null=True,
    )


class PersonalRelationshipTargetReference(PersonalRelationshipSourceReference):
    """Personal Relationship Target Reference model."""


class PersonalRelationshipAsserterReference(BaseReference):
    """Personal Relationship Asserter Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="personal_relationship_asserter_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        related_name="personal_relationship_asserter_reference_patient",
        on_delete=models.CASCADE,
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        related_name="personal_relationship_asserter_reference_related_person",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        related_name="personal_relationship_asserter_reference_practitioner",
        on_delete=models.CASCADE,
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="personal_relationship_asserter_reference_organization",
        on_delete=models.CASCADE,
        null=True,
    )


class PersonalRelationship(TimeStampedModel):
    """PersonalRelationship model."""

    source = models.ForeignKey(
        PersonalRelationshipSourceReference,
        related_name="personal_relationships_source",
        on_delete=models.CASCADE,
    )
    relationship_type = models.ForeignKey(
        CodeableConcept,
        related_name="personal_relationships_relationship_type",
        on_delete=models.CASCADE,
    )
    target = models.ForeignKey(
        PersonalRelationshipTargetReference,
        related_name="personal_relationships_target",
        on_delete=models.CASCADE,
    )
    period = models.ManyToManyField(
        Period,
        related_name="personal_relationships_period",
        blank=True,
    )
    confidence = models.ForeignKey(
        CodeableConcept,
        related_name="personal_relationships_confidence",
        on_delete=models.CASCADE,
        null=True,
    )
    asserter = models.ForeignKey(
        OrganizationReference,
        related_name="personal_relationships_asserter",
        on_delete=models.CASCADE,
        null=True,
    )
    group = models.ManyToManyField(
        "groups.GroupReference",
        related_name="personal_relationships_group",
        blank=True,
    )
