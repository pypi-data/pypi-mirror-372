"""Account models."""

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


class AccountSubjectReference(BaseReference):
    """Account subject reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="account_subject_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        related_name="account_subject_reference_patient",
        on_delete=models.CASCADE,
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        related_name="account_subject_reference_device",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        related_name="account_subject_reference_practitioner",
        on_delete=models.CASCADE,
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        related_name="account_subject_reference_practitioner_role",
        on_delete=models.CASCADE,
        null=True,
    )
    location = models.ForeignKey(
        "locations.Location",
        related_name="account_subject_reference_location",
        on_delete=models.CASCADE,
        null=True,
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        related_name="account_subject_reference_healthcare_service",
        on_delete=models.CASCADE,
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="account_subject_reference_organization",
        on_delete=models.CASCADE,
        null=True,
    )


class AccountCoverage(TimeStampedModel):
    """Account coverage model."""

    coverage = models.ForeignKey(
        "coverages.CoverageReference",
        related_name="account_coverage_coverage",
        on_delete=models.CASCADE,
        null=True,
    )
    priority = models.PositiveIntegerField(null=True)


class AccountsGuarantorPartyReference(BaseReference):
    """Account guarantor party reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="accounts_guarantor_party_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        related_name="accounts_guarantor_party_reference_patient",
        on_delete=models.CASCADE,
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        related_name="accounts_guarantor_party_reference_related_person",
        on_delete=models.CASCADE,
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="accounts_guarantor_party_reference_organization",
        on_delete=models.CASCADE,
        null=True,
    )


class AccountGuarantor(TimeStampedModel):
    """Account guarantor model."""

    party = models.ForeignKey(
        AccountsGuarantorPartyReference,
        related_name="account_guarantor_party",
        on_delete=models.CASCADE,
        null=True,
    )
    on_hold = models.BooleanField(default=False)
    period = models.ForeignKey(
        Period,
        related_name="account_guarantor_period",
        on_delete=models.CASCADE,
        null=True,
    )


class AccountDiagnosis(TimeStampedModel):
    """Account diagnosis model."""

    sequence = models.PositiveIntegerField(null=True)
    condition = models.ForeignKey(
        "conditions.ConditionCodeableReference",
        related_name="account_diagnosis_condition",
        on_delete=models.CASCADE,
        null=True,
    )
    date_of_diagnosis = models.DateTimeField(null=True)
    type = models.ManyToManyField(
        CodeableConcept, related_name="account_diagnosis_type", blank=True
    )
    on_admission = models.BooleanField(default=False)
    package_code = models.ManyToManyField(
        CodeableConcept, related_name="account_diagnosis_package_code", blank=True
    )


class AccountProcedure(TimeStampedModel):
    """Account procedure model."""

    sequence = models.PositiveIntegerField(null=True)
    code = models.ForeignKey(
        "procedures.ProcedureCodeableReference",
        related_name="account_procedure_code",
        on_delete=models.CASCADE,
        null=True,
    )
    date_of_service = models.DateTimeField(null=True)
    type = models.ManyToManyField(
        CodeableConcept, related_name="account_procedure_type", blank=True
    )
    package_code = models.ManyToManyField(
        CodeableConcept, related_name="account_procedure_package_code", blank=True
    )
    device = models.ManyToManyField(
        "devices.DeviceReference", related_name="account_procedure_device", blank=True
    )


class AccountRelatedAccount(TimeStampedModel):
    """Account related account model."""

    relationship = models.ForeignKey(
        CodeableConcept,
        related_name="account_related_account_relationship",
        on_delete=models.CASCADE,
        null=True,
    )
    account = models.ForeignKey(
        "AccountReference",
        related_name="account_related_account_reference",
        on_delete=models.CASCADE,
        null=True,
    )


class AccountBalance(TimeStampedModel):
    """Account balance model."""

    aggregate = models.ForeignKey(
        CodeableConcept,
        related_name="account_balance_aggregate",
        on_delete=models.CASCADE,
        null=True,
    )
    term = models.ForeignKey(
        CodeableConcept,
        related_name="account_balance_term",
        on_delete=models.CASCADE,
        null=True,
    )
    estimated = models.BooleanField(default=False)
    amount = models.ForeignKey(
        Money,
        related_name="account_balance_amount",
        on_delete=models.CASCADE,
        null=True,
    )


class Account(TimeStampedModel):
    """Account model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="accounts_identifier", blank=True
    )
    status = models.CharField(
        max_length=255, choices=choices.AccountStatus.choices, null=True
    )
    billing_status = models.ForeignKey(
        CodeableConcept,
        related_name="accounts_billing_status",
        null=True,
        on_delete=models.CASCADE,
    )
    type = models.ForeignKey(
        CodeableConcept,
        related_name="accounts_type",
        null=True,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255, null=True)
    subject = models.ManyToManyField(
        AccountSubjectReference, related_name="accounts_subject", blank=True
    )
    service_period = models.ForeignKey(
        Period,
        related_name="accounts_service_period",
        on_delete=models.CASCADE,
        null=True,
    )
    covers = models.ManyToManyField(
        "encounters.EncounterEpisodeOfCareReference",
        related_name="accounts_covers",
        blank=True,
    )
    coverage = models.ManyToManyField(
        AccountCoverage, related_name="accounts_coverage", blank=True
    )
    owner = models.ForeignKey(
        OrganizationReference,
        related_name="accounts_owner",
        on_delete=models.CASCADE,
        null=True,
    )
    description = models.TextField(null=True)
    guarantor = models.ManyToManyField(
        AccountGuarantor, related_name="accounts_guarantor", blank=True
    )
    diagnosis = models.ManyToManyField(
        AccountDiagnosis, related_name="accounts_diagnosis", blank=True
    )
    procedure = models.ManyToManyField(
        AccountProcedure, related_name="accounts_procedure", blank=True
    )
    related_account = models.ManyToManyField(
        AccountRelatedAccount, related_name="accounts_related_account", blank=True
    )
    currency = models.ForeignKey(
        CodeableConcept,
        related_name="accounts_currency",
        null=True,
        on_delete=models.CASCADE,
    )
    balance = models.ManyToManyField(
        AccountBalance, related_name="accounts_balance", blank=True
    )
    calculated_at = models.DateTimeField(null=True)


class AccountReference(BaseReference):
    """Account reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="account_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    account = models.ForeignKey(
        Account,
        related_name="account_reference_account",
        on_delete=models.CASCADE,
        null=True,
    )
