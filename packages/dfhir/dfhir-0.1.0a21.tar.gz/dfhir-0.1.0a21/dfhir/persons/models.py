"""Person model."""

from django.db import models

from dfhir.base.choices import GenderChoices
from dfhir.base.models import (
    Address,
    Attachment,
    BaseReference,
    CodeableConcept,
    Communication,
    ContactPoint,
    HumanName,
    Identifier,
    OrganizationReference,
    TimeStampedModel,
)

from . import choices


class PersonLinkTargetReference(BaseReference):
    """Model definition for PersonLinkTargetReference."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="person_link_target_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    person = models.ForeignKey(
        "Person",
        related_name="person_link_target_reference_person",
        on_delete=models.CASCADE,
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        related_name="person_link_target_reference_patient",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        related_name="person_link_target_reference_practitioner",
        on_delete=models.CASCADE,
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        related_name="person_link_target_reference_related_person",
        on_delete=models.CASCADE,
        null=True,
    )


class PersonLink(TimeStampedModel):
    """Model definition for PersonLink."""

    target = models.ForeignKey(
        PersonLinkTargetReference,
        related_name="person_link_target",
        on_delete=models.CASCADE,
    )
    assurance = models.CharField(
        max_length=255, choices=choices.LinkAssuranceChoices.choices, null=True
    )


class Person(TimeStampedModel):
    """Model definition for Person."""

    identifier = models.ManyToManyField(
        Identifier, related_name="persons_identifier", blank=True
    )
    active = models.BooleanField(default=True)
    name = models.ManyToManyField(HumanName, related_name="persons_name", blank=True)
    telecom = models.ManyToManyField(
        ContactPoint, related_name="persons_telecom", blank=True
    )
    gender = models.CharField(max_length=255, choices=GenderChoices.choices, null=True)
    birth_date = models.DateField(null=True)
    deceased_boolean = models.BooleanField(null=True)
    deceased_date_time = models.DateTimeField(null=True)
    address = models.ManyToManyField(
        Address, related_name="persons_address", blank=True
    )
    marital_status = models.ForeignKey(
        CodeableConcept,
        related_name="persons_marital_status",
        on_delete=models.CASCADE,
        null=True,
    )
    photo = models.ManyToManyField(Attachment, related_name="persons_photo", blank=True)
    communication = models.ManyToManyField(
        Communication, related_name="persons_communication", blank=True
    )
    managing_organization = models.ForeignKey(
        OrganizationReference,
        related_name="persons_managing_organization",
        on_delete=models.CASCADE,
        null=True,
    )
    link = models.ManyToManyField(PersonLink, related_name="persons_link", blank=True)


class PersonReference(BaseReference):
    """Model definition for PersonReference."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="person_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    person = models.ForeignKey(
        Person,
        related_name="person_reference_person",
        on_delete=models.CASCADE,
        null=True,
    )
