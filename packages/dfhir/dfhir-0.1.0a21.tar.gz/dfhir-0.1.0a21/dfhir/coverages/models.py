"""Coverage models."""

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


class CoveragePaymentByPartyReference(BaseReference):
    """Coverage By Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="coverage_by_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="coverage_by_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="coverage_by_reference_related_person",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="coverage_by_reference_organization",
        null=True,
    )


class CoveragePaymentBy(TimeStampedModel):
    """Coverage Payment By model."""

    party = models.ForeignKey(
        CoveragePaymentByPartyReference,
        on_delete=models.DO_NOTHING,
        related_name="coverage_payment_by_party",
        null=True,
    )
    responsibility = models.CharField(
        max_length=255,
        null=True,
    )


class CoveragePolicyHolderReference(BaseReference):
    """Policy Holder Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="policy_holder_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="policy_holder_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="policy_holder_reference_related_person",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="policy_holder_reference_organization",
        null=True,
    )


class CoverageClass(TimeStampedModel):
    """Coverage Class model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="coverage_class_type",
        null=True,
    )
    value = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="coverage_class_value",
        null=True,
    )
    name = models.CharField(max_length=255, null=True)


class CoverageCostToBeneficiaryException(TimeStampedModel):
    """Coverage Cost To Beneficiary Exception model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="coverage_cost_to_beneficiary_exception_type",
        null=True,
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="coverage_cost_to_beneficiary_exception_period",
        null=True,
    )


class CoverageCostToBeneficiary(TimeStampedModel):
    """Coverage Cost To Beneficiary model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="coverage_cost_to_beneficiary_type",
        null=True,
    )
    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="coverage_cost_to_beneficiary_category",
        null=True,
    )
    network = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="coverage_cost_to_beneficiary_network",
        null=True,
    )
    unit = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="coverage_cost_to_beneficiary_unit",
        null=True,
    )
    term = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="coverage_cost_to_beneficiary_term",
        null=True,
    )
    value_quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.DO_NOTHING,
        related_name="coverage_cost_to_beneficiary_value_quantity",
        null=True,
    )
    value_money = models.ForeignKey(
        Money,
        on_delete=models.DO_NOTHING,
        related_name="coverage_cost_to_beneficiary_value_money",
        null=True,
    )
    exception = models.ManyToManyField(
        CoverageCostToBeneficiaryException,
        related_name="coverage_cost_to_beneficiary_exception",
        blank=True,
    )


class Coverage(TimeStampedModel):
    """Coverage model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="coverage_identifier",
        blank=True,
    )
    status = models.CharField(
        max_length=255, choices=choices.CoverageStatusChoices.choices
    )
    kind = models.CharField(max_length=255, choices=choices.CoverageKindChoices.choices)
    payment_by = models.ForeignKey(
        CoveragePaymentBy,
        on_delete=models.DO_NOTHING,
        related_name="coverage_payment_by",
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="coverage_type",
        null=True,
    )
    policy_holder = models.ForeignKey(
        CoveragePolicyHolderReference,
        on_delete=models.DO_NOTHING,
        related_name="coverage_policy_holder",
        null=True,
    )
    subscriber = models.ForeignKey(
        "patients.PatientRelatedPersonReference",
        on_delete=models.DO_NOTHING,
        related_name="coverage_subscriber",
        null=True,
    )
    subscriber_identifier = models.ManyToManyField(
        Identifier, related_name="coverage_subscriber_identifier", blank=True
    )
    beneficiary = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        related_name="coverage_beneficiary",
        null=True,
    )
    dependent = models.CharField(max_length=255, null=True)
    relationship = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="coverage_relationship",
        null=True,
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="coverage_period",
        null=True,
    )
    insurer = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        related_name="coverage_insurer",
        null=True,
    )
    klass = models.ManyToManyField(
        CoverageClass,
        related_name="coverage_class",
        blank=True,
    )
    order = models.IntegerField(null=True)
    network = models.CharField(max_length=255, null=True)
    cost_to_beneficiary = models.ManyToManyField(
        CoverageCostToBeneficiary,
        related_name="coverage_cost_to_beneficiary",
        blank=True,
    )
    subrogation = models.BooleanField(default=True)
    contract = models.ManyToManyField(
        "contracts.ContractReference",
        related_name="coverage_contract",
        blank=True,
    )
    # insurance_plan = models.ForeignKey(
    #     "insuranceplans.InsurancePlan",
    #     on_delete=models.DO_NOTHING,
    #     related_name="coverage_insurance_plan",
    #     null=True,
    # )


class CoverageReference(BaseReference):
    """Coverage reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="coverage_reference_identifier",
        null=True,
    )
    coverage = models.ForeignKey(
        Coverage,
        on_delete=models.DO_NOTHING,
        related_name="coverage_reference_coverage",
        null=True,
    )


class CoverageClaimResponseReference(BaseReference):
    """coverage claim response reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="coverage_claim_response_reference_identifier",
    )
    coverage = models.ForeignKey(
        Coverage,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="coverage_claim_response_reference_coverage",
    )
    claim_response = models.ForeignKey(
        "claimresponses.ClaimResponse",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="coverage_claim_response_reference_claim_response",
    )
