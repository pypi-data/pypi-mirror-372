"""Patient models."""

from django.db import models
from django.utils.translation import gettext_lazy as _

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
    OrganizationReference,
    Period,
    TimeStampedModel,
)

from . import choices


class PatientRelatedPersonReference(BaseReference):
    """Patient related person reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="patient_related_person_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
        related_name="patient_related_person_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="patient_related_person_reference_related_person",
        null=True,
    )


class PatientGroupReference(BaseReference):
    """Patient group reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="patient_group_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "Patient",
        on_delete=models.CASCADE,
        related_name="patient_group_reference_patient",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="patient_group_reference_group",
        null=True,
    )


class PatientContact(TimeStampedModel):
    """Patient contact model."""

    name = models.ForeignKey(
        HumanName,
        on_delete=models.CASCADE,
        related_name="patient_contact_name",
        null=True,
    )
    gender = models.CharField(
        max_length=20, choices=base_choices.GenderChoices.choices, null=True, blank=True
    )
    relationship = models.ManyToManyField(
        CodeableConcept, related_name="patient_contact_relationship", blank=True
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name="patient_contact_address",
        null=True,
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="patient_contact_period",
        null=True,
    )
    organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="patient_contact_organization",
    )
    telecom = models.ManyToManyField(
        ContactPoint, related_name="patient_contact_telecom", blank=True
    )


class PatientLink(TimeStampedModel):
    """Patient link model."""

    other = models.ForeignKey(
        "PatientRelatedPersonReference",
        on_delete=models.CASCADE,
        related_name="patient_link_other",
        null=True,
    )
    type = models.CharField(
        max_length=20, choices=choices.PatientLinkChoices.choices, null=True, blank=True
    )


class Patient(TimeStampedModel):
    """Patient model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="patient_identifier", blank=True
    )
    name = models.ManyToManyField(HumanName, related_name="patient_name", blank=True)
    telecom = models.ManyToManyField(
        ContactPoint, related_name="patient_telecom", blank=True
    )
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20, choices=base_choices.GenderChoices.choices, null=True, blank=True
    )
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(_("email address"), unique=True, null=True)
    deceased_boolean = models.BooleanField(default=True)
    deceased_date_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    marital_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="patient_marital_status",
    )
    communication = models.ManyToManyField(
        Communication, related_name="patient_communication", blank=True
    )
    multiple_birth_boolean = models.BooleanField(default=False)
    multiple_birth_integer = models.IntegerField(null=True, blank=True)
    photo = models.ManyToManyField(Attachment, related_name="patient_photo", blank=True)
    contact = models.ManyToManyField(
        PatientContact, related_name="patient_contact", blank=True
    )
    general_practitioner = models.ManyToManyField(
        "practitioners.PractitionerOrganizationPractitionerRoleReference",
        related_name="patient_general_practitioner",
        blank=True,
    )
    managing_organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="patient_managing_organization",
    )
    address = models.ManyToManyField(
        Address, related_name="patient_address", blank=True
    )


class PatientReference(BaseReference):
    """Patient reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="patient_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="patient_reference_patient",
        null=True,
    )


class PatientOrganizationReference(BaseReference):
    """patient organization reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="patient_organization_reference_identifier",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        related_name="patient_organization_reference_patient",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        related_name="patient_organization_reference_organization",
        null=True,
    )


class PatientPractitionerReference(BaseReference):
    """patient practitioner reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="patient_practitioner_reference_identifier",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        related_name="patient_practitioner_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.SET_NULL,
        related_name="patient_practitioner_reference_practitioner",
        null=True,
    )
