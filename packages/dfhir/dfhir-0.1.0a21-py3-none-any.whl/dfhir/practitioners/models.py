"""Practitioner models."""

from django.db import models

from dfhir.base import choices as base_choices
from dfhir.base.models import (
    Address,
    Attachment,
    BaseReference,
    Communication,
    ContactPoint,
    HumanName,
    Identifier,
    Qualification,
    TimeStampedModel,
)


class PractitionerReference(BaseReference):
    """Practitioner reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="practitioner_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "Practitioner",
        on_delete=models.CASCADE,
        related_name="practitioner_reference_practitioner",
        null=True,
    )


class Practitioner(TimeStampedModel):
    """Practitioner model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="practitioner_identifier", blank=True
    )
    active = models.BooleanField(default=True)
    name = models.ManyToManyField(
        HumanName, related_name="practitioner_name", blank=True
    )
    telecom = models.ManyToManyField(
        ContactPoint, related_name="practitioner_telecom", blank=True
    )
    gender = models.CharField(
        max_length=20, choices=base_choices.GenderChoices.choices, null=True, blank=True
    )
    birth_date = models.DateField(null=True, blank=True)
    deceased_boolean = models.BooleanField(default=True)
    deceased_date_time = models.DateTimeField(null=True, blank=True)
    address = models.ManyToManyField(
        Address, related_name="practitioner_address", blank=True
    )
    photo = models.ManyToManyField(
        Attachment, related_name="practitioner_photo", blank=True
    )
    qualification = models.ManyToManyField(
        Qualification, related_name="practitioner_qualification", blank=True
    )
    communication = models.ManyToManyField(
        Communication, related_name="practitioner_communication", blank=True
    )


class PractitionerPractitionerRoleReference(BaseReference):
    """practitioner practitioner role reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="practitioner_practitioner_role_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.CASCADE,
        related_name="practitioner_practitioner_role_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="practitioner_practitioner_role_reference_practitioner_role",
        null=True,
    )


class PractitionerOrganizationPractitionerRoleReference(BaseReference):
    """practitioner organization practitioner role reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="practitioner_organization_practitioner_role_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.CASCADE,
        related_name="practitioner_organization_practitioner_role_reference_practitioner",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="practitioner_organization_practitioner_role_reference_organization",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="practitioner_organization_practitioner_role_reference_practitioner_role",
        null=True,
    )
