"""payment reconciliations models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)
from dfhir.paymentreconciliations.choices import (
    PaymentReconciliationOutcomeChoices,
    PaymentReconciliationProcessNoteChoices,
    PaymentReconciliationStatusChoices,
)


class OrganizationPractitionerPractitionerRoleReference(BaseReference):
    """payment reconciliations payment issuer reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        null=True,
        related_name="organization_practitioner_practitioner_role_reference_identifier",
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="organization_practitioner_practitioner_role_reference_organization",
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="organization_practitioner_practitioner_role_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="organization_practitioner_practitioner_role_reference_related_person",
    )


class PaymentReconciliationAllocationTargetReference(BaseReference):
    """payment reconciliations allocation target reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        null=True,
        related_name="payment_reconciliation_allocation_target_reference_identifier",
    )
    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_target_reference_claim",
    )
    account = models.ForeignKey(
        "accounts.Account",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_target_reference_account",
    )
    invoice = models.ForeignKey(
        "invoices.Invoice",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_target_reference_invoice",
    )
    charge_item = models.ForeignKey(
        "chargeitems.ChargeItem",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_target_reference_charge_item",
    )
    encounter = models.ForeignKey(
        "encounters.Encounter",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_target_reference_encounter",
    )
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_target_reference_contract",
    )


class PaymentReconciliationPaymentIssuerReference(BaseReference):
    """payment reconciliations payment issuer reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        null=True,
        related_name="payment_reconciliation_payment_issuer_reference_identifier",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_payment_issuer_reference_organization",
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_payment_issuer_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_payment_issuer_reference_related_person",
    )


class PaymentReconciliationAllocation(TimeStampedModel):
    """payment reconciliations allocation model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_identifier",
    )
    predecessor = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_predecessor",
    )
    target = models.ForeignKey(
        PaymentReconciliationAllocationTargetReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_target",
    )
    target_item_string = models.CharField(max_length=255, null=True)
    target_item_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_target_item_identifier",
    )
    target_item_positive_int = models.PositiveIntegerField(null=True)
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_encounter",
    )
    account = models.ForeignKey(
        "accounts.AccountReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_account",
    )
    type = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_type",
    )
    submitter = models.ForeignKey(
        OrganizationPractitionerPractitionerRoleReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_submitter",
    )
    response = models.ForeignKey(
        "claimresponses.ClaimResponse",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_response",
    )
    date = models.DateField(null=True)
    responsible = models.ForeignKey(
        "practitionerroles.PractitionerRoleReference",
        on_delete=models.CASCADE,
        null=True,
        related_name="payment_reconciliation_allocation_responsible",
    )
    payee = models.ForeignKey(
        OrganizationPractitionerPractitionerRoleReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_payee",
    )
    amount = models.ForeignKey(
        "base.Money",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_allocation_amount",
    )


class PaymentReconciliationProcessNote(TimeStampedModel):
    """payment reconciliations process note model."""

    type = models.CharField(
        max_length=255,
        null=True,
        choices=PaymentReconciliationProcessNoteChoices.choices,
    )
    text = models.CharField(max_length=255, null=True)


class PaymentReconciliation(TimeStampedModel):
    """payment reconciliations model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="payment_reconciliation_identifier", blank=True
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_type",
    )
    status = models.CharField(
        max_length=255, null=True, choices=PaymentReconciliationStatusChoices.choices
    )
    kind = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_kind",
    )
    period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_period",
    )
    created = models.DateTimeField(null=True)
    enterer = models.ForeignKey(
        OrganizationPractitionerPractitionerRoleReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_enterer",
    )
    issuer_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_issuer_type",
    )
    payment_issuer = models.ForeignKey(
        PaymentReconciliationPaymentIssuerReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_payment_issuer",
    )
    request = models.ForeignKey(
        "tasks.TaskReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_request",
    )
    requestor = models.ForeignKey(  # codespell:ignore requestor
        OrganizationPractitionerPractitionerRoleReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_requestor",
    )
    outcome = models.CharField(
        max_length=255, null=True, choices=PaymentReconciliationOutcomeChoices.choices
    )
    disposition = models.CharField(max_length=255, null=True)
    date = models.DateField(null=True)
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_location",
    )
    method = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_method",
    )
    card_brand = models.CharField(max_length=255, null=True)
    account_number = models.CharField(max_length=255, null=True)
    expiration_date = models.DateField(null=True)
    processor = models.CharField(max_length=255, null=True)
    reference_number = models.CharField(max_length=255, null=True)
    authorization = models.DateField(null=True)
    tendered_amount = models.ForeignKey(
        "base.Money",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_tendered_amount",
    )
    returned_amount = models.ForeignKey(
        "base.Money",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_returned_amount",
    )
    amount = models.ForeignKey(
        "base.Money",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_amount",
    )
    payment_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_payment_identifier",
    )
    allocation = models.ManyToManyField(
        PaymentReconciliationAllocation,
        related_name="payment_reconciliation_allocation",
        blank=True,
    )
    form_code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_form_code",
    )
    process_note = models.ManyToManyField(
        PaymentReconciliationProcessNote,
        related_name="payment_reconciliation_process_note",
        blank=True,
    )


class PaymentReconciliationReference(BaseReference):
    """payment reconciliations reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_reference_identifier",
    )
    payment_reconciliation = models.ForeignKey(
        PaymentReconciliation,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="payment_reconciliation_reference_payment_reconciliation",
    )
