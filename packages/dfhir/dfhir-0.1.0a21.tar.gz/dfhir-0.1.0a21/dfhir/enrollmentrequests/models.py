"""Enrollment Requests Models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    Identifier,
    OrganizationReference,
    TimeStampedModel,
)

from . import choices


class EnrollmentRequestProviderReference(BaseReference):
    """Enrollment Request Provider Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="enrollment_request_provider_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="enrollment_request_provider_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="enrollment_request_provider_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="enrollment_request_provider_reference_organization",
        null=True,
    )


class EnrollmentRequest(TimeStampedModel):
    """Enrollment request model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="enrollment_request_identifier",
        blank=True,
    )
    status = models.CharField(
        max_length=255,
        choices=choices.EnrollmentRequestStatus.choices,
        null=True,
    )
    created = models.DateTimeField(null=True)
    insurer = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="enrollment_request_insurer",
        null=True,
    )
    provider = models.ForeignKey(
        EnrollmentRequestProviderReference,
        on_delete=models.CASCADE,
        related_name="enrollment_request_provider",
        null=True,
    )
    candidate = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.CASCADE,
        related_name="enrollment_request_candidate",
        null=True,
    )
    coverage = models.ForeignKey(
        "coverages.CoverageReference",
        on_delete=models.CASCADE,
        related_name="enrollment_request_coverage",
        null=True,
    )


class EnrollmentRequestsReference(BaseReference):
    """Enrollment Requests Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="enrollment_requests_reference_identifier",
        null=True,
    )
    enrollment_request = models.ForeignKey(
        EnrollmentRequest,
        on_delete=models.CASCADE,
        related_name="enrollment_requests_reference_enrollment_request",
        null=True,
    )
