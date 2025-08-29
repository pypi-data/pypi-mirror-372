"""EnrollmentResponses models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    Identifier,
    OrganizationReference,
    TimeStampedModel,
)

from . import choices


class EnrollmentResponseRequestProviderReference(BaseReference):
    """EnrollmentResponse request provider reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="enrollment_response_request_provider_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        related_name="enrollment_response_request_provider_reference_practitioner",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        related_name="enrollment_response_request_provider_reference_practitioner_role",
        on_delete=models.CASCADE,
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="enrollment_response_request_provider_reference_organization",
        on_delete=models.CASCADE,
        null=True,
    )


class EnrollmentResponse(TimeStampedModel):
    """EnrollmentResponse model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="enrollment_response_identifier",
        blank=True,
    )
    status = models.CharField(
        max_length=50,
        choices=choices.EnrollmentResponseStatus.choices,
        null=True,
    )
    request = models.ForeignKey(
        "enrollmentrequests.EnrollmentRequest",
        related_name="enrollment_response_request",
        on_delete=models.CASCADE,
        null=True,
    )
    outcome = models.CharField(
        max_length=50,
        choices=choices.EnrollmentResponseOutcome.choices,
        null=True,
    )
    disposition = models.TextField(null=True)
    created = models.DateTimeField(auto_created=True, null=True)
    organization = models.ForeignKey(
        OrganizationReference,
        related_name="enrollment_response_organization",
        on_delete=models.CASCADE,
        null=True,
    )
    request_provider = models.ForeignKey(
        EnrollmentResponseRequestProviderReference,
        related_name="enrollment_response_request_provider",
        on_delete=models.CASCADE,
        null=True,
    )
