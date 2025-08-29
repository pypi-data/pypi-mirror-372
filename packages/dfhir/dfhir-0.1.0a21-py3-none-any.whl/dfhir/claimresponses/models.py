"""Claim responses model."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    Address,
    Attachment,
    BaseReference,
    CodeableConcept,
    Identifier,
    Money,
    OrganizationReference,
    Period,
    Quantity,
    SimpleQuantity,
    TimeStampedModel,
)

from . import choices


class ClaimResponseRequestorReference(BaseReference):
    """Claim response requestor model."""  # codespell:ignore requestor

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_response_requestor_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="claim_response_requestor_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="claim_response_requestor_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="claim_response_requestor_organization",
        null=True,
    )


class ClaimResponseEvent(TimeStampedModel):
    """Claim response event model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_event_type",
        null=True,
    )
    when_date_time = models.DateTimeField(null=True)
    when_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="claim_response_event_when_period",
        null=True,
    )


class ClaimResponseItemReviewOutcome(TimeStampedModel):
    """Claim response item review outcome model."""

    decision = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_item_review_outcome_decision",
        null=True,
    )
    reason = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_response_item_review_outcome_reason",
        blank=True,
    )
    pre_auth_ref = models.CharField(max_length=255, null=True)
    pre_auth_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="claim_response_item_review_outcome_pre_auth_period",
        null=True,
    )


class ClaimResponseItemAdjudication(TimeStampedModel):
    """Claim response item adjudication model."""

    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_item_adjudication_category",
        null=True,
    )
    reason = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_item_adjudication_reason",
        null=True,
    )
    amount = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_item_adjudication_amount",
        null=True,
    )
    quantity = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        related_name="claim_response_item_adjudication_quantity",
        null=True,
    )


class ClaimResponseItemDetailSubDetail(TimeStampedModel):
    """Claim response item detail sub detail model."""

    sub_detail_sequence = models.PositiveIntegerField()
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="claim_response_item_detail_sub_detail_trace_number",
        blank=True,
    )
    note_number = ArrayField(models.PositiveIntegerField(), null=True)
    review_outcome = models.ForeignKey(
        ClaimResponseItemReviewOutcome,
        on_delete=models.CASCADE,
        related_name="claim_response_item_detail_sub_detail_review_outcome",
        null=True,
    )
    adjudication = models.ManyToManyField(
        ClaimResponseItemAdjudication,
        related_name="claim_response_item_detail_sub_detail_adjudication",
        blank=True,
    )


class ClaimResponseItemDetail(TimeStampedModel):
    """Claim response item detail model."""

    detail_sequence = models.PositiveIntegerField()
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="claim_response_item_detail_trace_number",
        blank=True,
    )
    note_number = ArrayField(models.PositiveIntegerField(), null=True)
    review_outcome = models.ForeignKey(
        ClaimResponseItemReviewOutcome,
        on_delete=models.CASCADE,
        related_name="claim_response_item_detail_review_outcome",
        null=True,
    )
    adjudication = models.ManyToManyField(
        ClaimResponseItemAdjudication,
        related_name="claim_response_item_detail_adjudication",
        blank=True,
    )
    sub_detail = models.ManyToManyField(
        ClaimResponseItemDetailSubDetail,
        related_name="claim_response_item_detail_sub_detail",
        blank=True,
    )


class ClaimResponseItem(TimeStampedModel):
    """Claim response item model."""

    item_sequence = models.PositiveIntegerField()
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="claim_response_item_trace_number",
        blank=True,
    )
    note_number = ArrayField(models.PositiveIntegerField(), null=True)
    review_outcome = models.ForeignKey(
        ClaimResponseItemReviewOutcome,
        on_delete=models.CASCADE,
        related_name="claim_response_item_review_outcome",
        null=True,
    )
    adjudication = models.ManyToManyField(
        ClaimResponseItemAdjudication,
        related_name="claim_response_item_adjudication",
        blank=True,
    )
    detail = models.ManyToManyField(
        ClaimResponseItemDetail,
        related_name="claim_response_item_detail",
        blank=True,
    )


class ClaimResponseAddItemProviderReference(BaseReference):
    """Claim response add item provider reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_provider_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_provider_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_provider_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_provider_reference_organization",
        null=True,
    )


class ClaimResponseAddItemRequestReference(BaseReference):
    """Claim response add item request reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_request_reference_identifier",
        null=True,
    )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_request_reference_device_request",
        null=True,
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_request_reference_medication_request",
        null=True,
    )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_request_reference_nutrition_order",
        null=True,
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_request_reference_service_request",
        null=True,
    )
    supply_request = models.ForeignKey(
        "supplyrequests.SupplyRequest",
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_request_reference_supply_request",
        null=True,
    )
    vision_prescription = models.ForeignKey(
        "visionprescriptions.VisionPrescription",
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_request_reference_vision_prescription",
        null=True,
    )


class ClaimResponseAddItemBodySite(TimeStampedModel):
    """Claim response add item body site model."""

    site = models.ManyToManyField(
        "bodystructures.BodyStructureCodeableReference",
        related_name="claim_response_add_item_body_site_body_site",
        blank=True,
    )
    sub_site = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_response_add_item_body_site_sub_site",
        blank=True,
    )


class ClaimResponseAddItemDetailSubDetail(TimeStampedModel):
    """Claim response add item detail sub detail model."""

    trace_number = models.ManyToManyField(
        Identifier,
        related_name="claim_response_add_item_detail_sub_detail_trace_number",
        blank=True,
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_sub_detail_revenue",
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_sub_detail_product_or_service",
        null=True,
    )
    product_or_service_end = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_sub_detail_product_or_service_end",
        null=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_response_add_item_detail_sub_detail_modifier",
        blank=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_sub_detail_quantity",
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_sub_detail_unit_price",
        null=True,
    )
    factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_sub_detail_tax",
        null=True,
    )
    net = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_sub_detail_net",
        null=True,
    )
    note_number = ArrayField(models.PositiveIntegerField(), null=True)
    review_outcome = models.ForeignKey(
        ClaimResponseItemReviewOutcome,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_sub_detail_review_outcome",
        null=True,
    )
    adjudication = models.ManyToManyField(
        ClaimResponseItemAdjudication,
        related_name="claim_response_add_item_detail_sub_detail_adjudication",
        blank=True,
    )


class ClaimResponseAddItemDetail(TimeStampedModel):
    """Claim response add item detail model."""

    trace_number = models.ManyToManyField(
        Identifier,
        related_name="claim_response_add_item_detail_trace_number",
        blank=True,
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_revenue",
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_product_or_service",
        null=True,
    )
    product_or_service_end = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_product_or_service_end",
        null=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_response_add_item_detail_modifier",
        blank=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_quantity",
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_unit_price",
        null=True,
    )
    factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_tax",
        null=True,
    )
    net = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_net",
        null=True,
    )
    note_number = ArrayField(models.PositiveIntegerField(), null=True)
    review_outcome = models.ForeignKey(
        ClaimResponseItemReviewOutcome,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_detail_review_outcome",
        null=True,
    )
    adjudication = models.ManyToManyField(
        ClaimResponseItemAdjudication,
        related_name="claim_response_add_item_detail_adjudication",
        blank=True,
    )
    sub_detail = models.ManyToManyField(
        ClaimResponseAddItemDetailSubDetail,
        related_name="claim_response_add_item_detail_sub_detail",
        blank=True,
    )


class ClaimResponseAddItem(TimeStampedModel):
    """Claim response add item model."""

    item_sequence = ArrayField(models.PositiveIntegerField(), null=True)
    detail_sequence = ArrayField(models.PositiveIntegerField(), null=True)
    sub_detail_sequence = ArrayField(models.PositiveIntegerField(), null=True)
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="claim_response_add_item_trace_number",
        blank=True,
    )
    provider = models.ManyToManyField(
        ClaimResponseAddItemProviderReference,
        related_name="claim_response_add_item_provider",
        blank=True,
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_revenue",
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_product_or_service",
        null=True,
    )
    provider_or_service_end = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_provider_or_service_end",
        null=True,
    )
    request = models.ManyToManyField(
        ClaimResponseAddItemRequestReference,
        related_name="claim_response_add_item_request",
        blank=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_response_add_item_modifier",
        blank=True,
    )
    program_code = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_response_add_item_program_code",
        blank=True,
    )
    serviced_date = models.DateField(null=True)
    serviced_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_serviced_period",
        null=True,
    )
    location_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_location_codeable_concept",
        null=True,
    )
    location_address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_location_address",
        null=True,
    )
    location_reference = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_location_reference",
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_quantity",
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_unit_price",
        null=True,
    )
    factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_tax",
        null=True,
    )
    net = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_net",
        null=True,
    )
    body_site = models.ManyToManyField(
        ClaimResponseAddItemBodySite,
        related_name="claim_response_add_item_body_site",
        blank=True,
    )
    note_number = ArrayField(models.PositiveIntegerField(), null=True)
    review_outcome = models.ForeignKey(
        ClaimResponseItemReviewOutcome,
        on_delete=models.CASCADE,
        related_name="claim_response_add_item_review_outcome",
        null=True,
    )
    adjudication = models.ManyToManyField(
        ClaimResponseItemAdjudication,
        related_name="claim_response_add_item_adjudication",
        blank=True,
    )
    detail = models.ManyToManyField(
        ClaimResponseAddItemDetail,
        related_name="claim_response_add_item_detail",
        blank=True,
    )


class ClaimResponseTotal(TimeStampedModel):
    """Claim response total model."""

    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_total_category",
        null=True,
    )
    amount = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_total_amount",
        null=True,
    )


class ClaimResponsePayment(TimeStampedModel):
    """Claim response payment model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_payment_type",
        null=True,
    )
    adjustment = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_payment_adjustment",
        null=True,
    )
    adjustment_reason = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_payment_adjustment_reason",
        null=True,
    )
    date = models.DateField(null=True)
    amount = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="claim_response_payment_amount",
        null=True,
    )
    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_response_payment_identifier",
        null=True,
    )


class ClaimResponseProcessNote(TimeStampedModel):
    """Claim response process note model."""

    number = models.PositiveIntegerField(null=True)
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_process_note_type",
        null=True,
    )
    text = models.TextField(null=True)
    language = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_process_note_language",
        null=True,
    )


class ClaimResponseInsurance(TimeStampedModel):
    """Claim response insurance model."""

    sequence = models.PositiveIntegerField()
    focal = models.BooleanField()
    coverage = models.ForeignKey(
        "coverages.CoverageReference",
        on_delete=models.CASCADE,
        related_name="claim_response_insurance_coverage",
        null=True,
    )
    business_arrangement = models.CharField(max_length=255, null=True)
    claim_response = models.ForeignKey(
        "ClaimResponseReference",
        on_delete=models.CASCADE,
        related_name="claim_response_insurance_claim_response",
        null=True,
    )


class ClaimResponseError(TimeStampedModel):
    """Claim response error model."""

    item_sequence = models.PositiveIntegerField(null=True)
    detail_sequence = models.PositiveIntegerField(null=True)
    sub_detail_sequence = models.PositiveIntegerField(null=True)
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_error_code",
        null=True,
    )
    expression = ArrayField(models.CharField(max_length=255), null=True)


class ClaimResponse(TimeStampedModel):
    """Claim response model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="claim_response_identifier", blank=True
    )
    trace_number = models.ManyToManyField(
        Identifier, related_name="claim_response_trace_number", blank=True
    )
    status = models.CharField(
        max_length=255,
        choices=choices.ClaimResponseStatus.choices,
        default=choices.ClaimResponseStatus.ACTIVE,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_type",
        null=True,
    )
    sub_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_sub_type",
        null=True,
    )
    use = models.CharField(
        max_length=255,
        choices=choices.ClaimResponseUse.choices,
        default=choices.ClaimResponseUse.CLAIM,
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.CASCADE,
        related_name="claim_response_patient",
        null=True,
    )
    created = models.DateTimeField(null=True)
    insurer = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="claim_response_insurer",
        null=True,
    )
    requestor = models.ForeignKey(  # codespell:ignore requestor
        ClaimResponseRequestorReference,
        on_delete=models.CASCADE,
        related_name="claim_response_requestor",  # codespell:ignore requestor
        null=True,
    )
    request = models.ForeignKey(
        "claims.ClaimReference",
        on_delete=models.CASCADE,
        related_name="claim_response_request",
        null=True,
    )
    outcome = models.CharField(
        max_length=255, choices=choices.ClaimResponseOutcome.choices, null=True
    )
    decision = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_decision",
        null=True,
    )
    disposition = models.TextField(null=True)
    pre_auth_ref = models.CharField(max_length=255, null=True)
    pre_auth_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="claim_response_pre_auth_period",
        null=True,
    )
    event = models.ManyToManyField(
        ClaimResponseEvent, related_name="claim_response_event", blank=True
    )
    payee_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_payee_type",
        null=True,
    )
    encounter = models.ManyToManyField(
        "encounters.EncounterReference",
        related_name="claim_response_encounter",
        blank=True,
    )
    diagnosis_related_group = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_diagnosis_related_group",
        null=True,
    )
    item = models.ManyToManyField(
        ClaimResponseItem, related_name="claim_response_item", blank=True
    )
    add_item = models.ManyToManyField(
        ClaimResponseAddItem, related_name="claim_response_add_item", blank=True
    )
    adjudication = models.ManyToManyField(
        ClaimResponseItemAdjudication,
        related_name="claim_response_adjudication",
        blank=True,
    )
    total = models.ManyToManyField(
        ClaimResponseTotal, related_name="claim_response_total", blank=True
    )
    payment = models.ForeignKey(
        ClaimResponsePayment,
        on_delete=models.CASCADE,
        related_name="claim_response_payment",
        null=True,
    )
    funds_reserve = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_funds_reserve",
        null=True,
    )
    form_code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_response_form_code",
        null=True,
    )
    form = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="claim_response_form",
        null=True,
    )
    process_note = models.ManyToManyField(
        ClaimResponseProcessNote, related_name="claim_response_process_note", blank=True
    )
    # communication_request = models.ManyToManyField(
    #     "communicationrequests.CommunicationRequestReference",
    #     related_name="claim_response_communication_request",
    #     blank=True,
    # )
    insurance = models.ManyToManyField(
        ClaimResponseInsurance, related_name="claim_response_insurance", blank=True
    )
    error = models.ManyToManyField(
        ClaimResponseError, related_name="claim_response_error", blank=True
    )


class ClaimResponseReference(BaseReference):
    """Claim response reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_response_reference_identifier",
        null=True,
    )
    claim_response = models.ForeignKey(
        ClaimResponse,
        on_delete=models.CASCADE,
        related_name="claim_response_reference_claim_response",
        null=True,
    )
