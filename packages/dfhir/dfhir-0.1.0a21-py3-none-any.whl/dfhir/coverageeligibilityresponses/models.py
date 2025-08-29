"""CoverageEligibilityResponses models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Money,
    OrganizationReference,
    Period,
    TimeStampedModel,
)

from . import choices


class CoverageEligibilityResponseEvent(TimeStampedModel):
    """Coverage Eligibility Response Event model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_event_type",
    )
    when_date_time = models.DateTimeField(null=True)
    when_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_event_when_period",
        null=True,
    )


class CoverageEligibilityResponseInsuranceItemBenefit(TimeStampedModel):
    """Coverage Eligibility Response Insurance Item Benefit model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurance_item_benefit_type",
    )
    allowed_string = models.CharField(max_length=255, null=True)
    allowed_unsigned_int = models.PositiveIntegerField(null=True)
    allowed_money = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurance_item_benefit_allowed_money",
        null=True,
    )
    used_string = models.CharField(max_length=255, null=True)
    used_unsigned_int = models.PositiveIntegerField(null=True)
    used_money = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurance_item_benefit_used_money",
        null=True,
    )


class CoverageEligibilityResponseInsuranceItem(TimeStampedModel):
    """Coverage Eligibility Response Insurance Item model."""

    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurance_item_category",
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurance_item_product_or_service",
        null=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="coverage_eligibility_response_insurance_item_modifier",
    )
    provider = models.ForeignKey(
        "practitioners.PractitionerPractitionerRoleReference",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurance_item_provider",
        null=True,
    )
    excluded = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    network = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurance_item_network",
        null=True,
    )
    unit = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurance_item_unit_price",
        null=True,
    )
    term = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurance_item_term",
        null=True,
    )
    benefit = models.ManyToManyField(
        CoverageEligibilityResponseInsuranceItemBenefit,
        related_name="coverage_eligibility_response_insurance_item_benefit",
        blank=True,
    )
    authorization_required = models.BooleanField(default=False)
    authorization_supporting = models.ManyToManyField(
        CodeableConcept,
        related_name="coverage_eligibility_response_insurance_item_authorization_supporting",
        blank=True,
    )
    authorization_url = models.URLField(null=True)


class CoverageEligibilityResponseError(TimeStampedModel):
    """Coverage Eligibility Response Error model."""

    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_error_code",
        null=True,
    )
    expression = ArrayField(models.CharField(max_length=255), null=True)


class CoverageEligibilityResponseInsurance(TimeStampedModel):
    """Coverage Eligibility Response Insurance model."""

    coverage = models.ForeignKey(
        "coverages.CoverageReference",
        on_delete=models.CASCADE,
        null=True,
        related_name="coverage_eligibility_response_insurance_coverage",
    )
    inforce = models.BooleanField(default=False)  # codespell:ignore inforce
    benefit_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurance_benefit_period",
        null=True,
    )
    item = models.ManyToManyField(
        CoverageEligibilityResponseInsuranceItem,
        related_name="coverage_eligibility_response_insurance_item",
        blank=True,
    )


class CoverageEligibilityResponseRequesterReference(BaseReference):
    """Coverage Eligibility Response Requester Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_requester_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_requester_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_requester_reference_practitioner_role",
        null=True,
    )

    organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_requester_reference_organization",
        null=True,
    )


class CoverageEligibilityResponse(TimeStampedModel):
    """Coverage Eligibility Responses model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="coverage_eligibility_response_identifier",
        blank=True,
    )
    status = models.CharField(
        max_length=255,
        choices=choices.CoverageEligibilityResponseStatus.choices,
        default=choices.CoverageEligibilityResponseStatus.ACTIVE,
    )
    purpose = ArrayField(
        models.CharField(
            max_length=255,
            choices=choices.CoverageEligibilityResponsePurpose.choices,
            default=choices.CoverageEligibilityResponsePurpose.AUTH_REQUIREMENTS,
        )
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_patient",
    )
    event = models.ManyToManyField(
        CoverageEligibilityResponseEvent,
        related_name="coverage_eligibility_response_event",
        blank=True,
    )
    serviced_date = models.DateField(null=True)
    serviced_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_serviced_period",
        null=True,
    )
    created = models.DateTimeField(null=True)
    requestor = models.ForeignKey(  # codespell:ignore requestor
        CoverageEligibilityResponseRequesterReference,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_requestor",
        null=True,
    )
    # request = models.ForeignKey(
    #     "coverageeligibilityrequests.CoverageEligibilityRequestReference",
    #     on_delete=models.CASCADE,
    #     related_name="coverage_eligibility_response_request",
    #     null=True,
    # )
    outcome = models.CharField(
        max_length=255,
        choices=choices.CoverageEligibilityResponseOutcome.choices,
        default=choices.CoverageEligibilityResponseOutcome.QUEUED,
    )
    disposition = models.TextField(null=True)
    insurer = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_insurer",
    )
    insurance = models.ManyToManyField(
        CoverageEligibilityResponseInsurance,
        related_name="coverage_eligibility_response_insurance",
        blank=True,
    )
    pre_auth_ref = models.CharField(max_length=255, null=True)
    form = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_response_form",
        null=True,
    )
    error = models.ManyToManyField(
        CoverageEligibilityResponseError,
        related_name="coverage_eligibility_response_error",
        blank=True,
    )
