"""RelatedPersons models."""

from django.db import models

from dfhir.base import choices as base_choices
from dfhir.base.models import (
    Address,
    Attachment,
    BaseReference,
    CodeableConcept,
    Communication,
    ContactPoint,
    HumanName,
    Identifier,
    Period,
    TimeStampedModel,
)


class RelatedPerson(TimeStampedModel):
    """RelatedPerson model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="relatedpersons_identifier", blank=True
    )
    active = models.BooleanField(default=True)
    patient = models.ForeignKey(
        "patients.PatientReference",
        related_name="relatedpersons_patient",
        on_delete=models.CASCADE,
    )
    relationship = models.ManyToManyField(
        CodeableConcept, related_name="relatedpersons_relationship", blank=True
    )
    role = models.ManyToManyField(
        CodeableConcept, related_name="relatedpersons_role", blank=True
    )
    name = models.ManyToManyField(
        HumanName, related_name="relatedpersons_name", blank=True
    )
    telecom = models.ManyToManyField(
        ContactPoint, related_name="relatedpersons_telecom", blank=True
    )
    gender = models.CharField(
        max_length=20, choices=base_choices.GenderChoices.choices, null=True, blank=True
    )
    birth_date = models.DateField(null=True)
    address = models.ManyToManyField(
        Address, related_name="relatedpersons_address", blank=True
    )
    photo = models.ManyToManyField(
        Attachment, related_name="relatedpersons_photo", blank=True
    )
    period = models.ForeignKey(
        Period,
        related_name="relatedpersons_period",
        on_delete=models.CASCADE,
        null=True,
    )
    communication = models.ManyToManyField(
        Communication, related_name="relatedpersons_communication", blank=True
    )


class RelatedPersonReference(BaseReference):
    """RelatedPerson Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="related_person_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    related_person = models.ForeignKey(
        RelatedPerson,
        related_name="related_person_reference_related_person",
        on_delete=models.CASCADE,
        null=True,
    )
