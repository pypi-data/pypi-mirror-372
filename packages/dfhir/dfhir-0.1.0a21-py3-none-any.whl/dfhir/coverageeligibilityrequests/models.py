"""CoverageEligibilityRequests models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Money,
    OrganizationReference,
    Period,
    SimpleQuantity,
    TimeStampedModel,
)

from . import choices


class CoverageEligibilityRequestEvent(TimeStampedModel):
    """CoverageEligibilityRequestEvent model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_event_type",
        null=True,
    )
    when_date_time = models.DateTimeField(null=True)
    when_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_event_when_period",
        null=True,
    )


class CoverageEligibilityRequestSupportingInfoInformationReference(BaseReference):
    """CoverageEligibilityRequestSupportingInfoInformationReference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_supporting_info_information_reference_identifier",
        null=True,
    )


class CoverageEligibilityRequestSupportingInfo(TimeStampedModel):
    """CoverageEligibilityRequestSupportingInfo model."""

    sequence = models.IntegerField()
    information = models.ForeignKey(
        CoverageEligibilityRequestSupportingInfoInformationReference,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_supporting_info_information",
        null=True,
    )
    applies_to_all = models.BooleanField(default=False)


class CoverageEligibilityRequestInsurance(TimeStampedModel):
    """CoverageEligibilityRequestInsurance model."""

    focal = models.BooleanField(default=False)
    coverage = models.ForeignKey(
        "coverages.CoverageReference",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_insurance_coverage",
        null=True,
    )
    business_arrangement = models.CharField(max_length=255, null=True)


class CoverageEligibilityRequestItemDiagnosis(TimeStampedModel):
    """CoverageEligibilityRequestItemDiagnosis model."""

    diagnosis_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_item_diagnosis_codeable_concept",
        null=True,
    )
    diagnosis_reference = models.ForeignKey(
        "conditions.ConditionReference",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_item_diagnosis_reference",
        null=True,
    )


class CoverageEligibilityRequestItemDetailReference(BaseReference):
    """CoverageEligibilityRequestItemDetailReference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_item_detail_reference_identifier",
        null=True,
    )


class CoverageEligibilityRequestItem(TimeStampedModel):
    """CoverageEligibilityRequestItem model."""

    supporting_info_sequence = ArrayField(models.IntegerField(), null=True)
    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_item_category",
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_item_product_or_service",
        null=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="coverage_eligibility_request_item_modifier",
        blank=True,
    )
    provider = models.ForeignKey(
        "practitioners.PractitionerPractitionerRoleReference",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_item_provider",
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        null=True,
        related_name="coverage_eligibility_request_item_quantity",
    )
    unit_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        null=True,
        related_name="coverage_eligibility_request_item_unit_price",
    )
    facility = models.ForeignKey(
        "locations.LocationOrganizationReference",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_item_facility",
        null=True,
    )
    diagnosis = models.ManyToManyField(
        CoverageEligibilityRequestItemDiagnosis,
        related_name="coverage_eligibility_request_item_diagnosis",
        blank=True,
    )
    detail = models.ManyToManyField(
        CoverageEligibilityRequestItemDetailReference,
        related_name="coverage_eligibility_request_item_detail",
        blank=True,
    )


class CoverageEligibilityRequestProviderReference(BaseReference):
    """CoverageEligibilityRequestProviderReference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_provider_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_provider_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_provider_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_provider_reference_organization",
        null=True,
    )


class CoverageEligibilityRequest(TimeStampedModel):
    """CoverageEligibilityRequest model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="coverage_eligibility_request_identifier", blank=True
    )
    status = models.CharField(
        max_length=255, choices=choices.CoverageEligibilityRequestStatus.choices
    )
    priority = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_priority",
        null=True,
    )
    purpose = ArrayField(
        models.CharField(
            max_length=255, choices=choices.CoverageEligibilityRequestPurpose.choices
        ),
        null=True,
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_patient",
        null=True,
    )
    event = models.ManyToManyField(
        CoverageEligibilityRequestEvent,
        related_name="coverage_eligibility_request_event",
        blank=True,
    )
    service_date = models.DateField(null=True)
    service_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_service_period",
        null=True,
    )
    created = models.DateTimeField(null=True)
    enterer = models.ForeignKey(
        "practitioners.PractitionerPractitionerRoleReference",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_enterer",
        null=True,
    )
    provider = models.ForeignKey(
        CoverageEligibilityRequestProviderReference,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_provider",
        null=True,
    )
    insurer = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_insurer",
        null=True,
    )
    facility = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.CASCADE,
        related_name="coverage_eligibility_request_facility",
        null=True,
    )
    supporting_info = models.ManyToManyField(
        CoverageEligibilityRequestSupportingInfo,
        related_name="coverage_eligibility_request_supporting_info",
        blank=True,
    )
    insurance = models.ManyToManyField(
        CoverageEligibilityRequestInsurance,
        related_name="coverage_eligibility_request_insurance",
        blank=True,
    )
    item = models.ManyToManyField(
        CoverageEligibilityRequestItem,
        related_name="coverage_eligibility_request_item",
        blank=True,
    )
