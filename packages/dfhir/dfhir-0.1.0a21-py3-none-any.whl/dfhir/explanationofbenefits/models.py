"""Explanation of Benefits models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    Address,
    Attachment,
    BaseReference,
    CodeableConcept,
    Coding,
    Identifier,
    Money,
    OrganizationReference,
    Period,
    Quantity,
    Reference,
    SimpleQuantity,
    TimeStampedModel,
)

from . import choices


class ExplanationOfBenefitEntererReference(BaseReference):
    """Explanation of Benefit enterer reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_enterer_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_enterer_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_enterer_reference_practitioner_role",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_enterer_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_enterer_reference_related_person",
        null=True,
    )


class ExplanationOfBenefitProviderReference(BaseReference):
    """Explanation of Benefit provider reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_provider_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_provider_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_provider_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_provider_reference_organization",
        null=True,
    )


class ExplanationOfBenefitRelated(TimeStampedModel):
    """Explanation of Benefits related model."""

    claim = models.ForeignKey(
        "claims.ClaimReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_related_claim",
        null=True,
    )
    relationship = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_related_relationship",
        null=True,
    )
    reference = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_related_reference",
        null=True,
    )


class ExplanationOfBenefitPrescriptionReference(BaseReference):
    """Explanation of Benefit prescription reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_prescription_reference_identifier",
        null=True,
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_prescription_reference_medication_request",
        null=True,
    )
    vision_prescription = models.ForeignKey(
        "visionprescriptions.VisionPrescription",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_prescription_reference_vision_prescription",
        null=True,
    )


class ExplanationOfBenefitEvent(TimeStampedModel):
    """Explanation of Benefit event model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_event_code",
        null=True,
    )
    when_date_time = models.DateTimeField(null=True)
    when_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_event_when_period",
        null=True,
    )


class ExplanationOfBenefitPayeePartyReference(BaseReference):
    """Explanation of Benefit payee party reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payee_party_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payee_party_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payee_party_reference_related_person",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payee_party_reference_organization",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payee_party_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payee_party_reference_practitioner_role",
        null=True,
    )


class ExplanationOfBenefitPayee(TimeStampedModel):
    """Explanation of Benefit payee model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payee_type",
        null=True,
    )
    party = models.ForeignKey(
        ExplanationOfBenefitPayeePartyReference,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payee_party",
        null=True,
    )


class ExplanationOfBenefitCareTeam(TimeStampedModel):
    """Explanation of Benefit care team model."""

    sequence = models.PositiveIntegerField()
    provider = models.ForeignKey(
        ExplanationOfBenefitProviderReference,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_care_team_provider",
        null=True,
    )
    responsible = models.BooleanField(default=False)
    role = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_care_team_role",
        null=True,
    )
    specialty = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_care_team_qualification",
        null=True,
    )


class ExplanationOfBenefitSupportingInfo(TimeStampedModel):
    """Explanation of Benefit supporting info model."""

    sequence = models.PositiveIntegerField()
    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_supporting_info_category",
        null=True,
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_supporting_info_code",
        null=True,
    )
    timing_date = models.DateField(null=True)
    timing_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_supporting_info_timing_period",
        null=True,
    )
    value_boolean = models.BooleanField(null=True)
    value_string = models.CharField(max_length=255, null=True)
    value_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_supporting_info_value_quantity",
        null=True,
    )
    value_attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_supporting_info_value_attachment",
        null=True,
    )
    value_reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_supporting_info_value_reference",
        null=True,
    )
    value_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_supporting_info_value_identifier",
        null=True,
    )
    reason = models.ForeignKey(
        Coding,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_supporting_info_reason",
        null=True,
    )


class ExplanationOfBenefitDiagnosis(TimeStampedModel):
    """Explanation of Benefit diagnosis model."""

    sequence = models.PositiveIntegerField()
    diagnosis_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_diagnosis_diagnosis_codeable_concept",
        null=True,
    )
    diagnosis_reference = models.ForeignKey(
        "conditions.ConditionReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_diagnosis_diagnosis_reference",
        null=True,
    )
    type = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_diagnosis_type",
        blank=True,
    )
    on_admission = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_diagnosis_on_admission",
        null=True,
    )


class ExplanationOfBenefitProcedure(TimeStampedModel):
    """Explanation of Benefit procedure model."""

    sequence = models.PositiveIntegerField()
    type = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_procedure_type",
        blank=True,
    )
    date = models.DateTimeField()
    procedure_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_procedure_procedure_codeable_concept",
        null=True,
    )
    procedure_reference = models.ForeignKey(
        "procedures.ProcedureReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_procedure_procedure_reference",
        null=True,
    )
    udi = models.ManyToManyField(
        "devices.DeviceReference",
        related_name="explanation_of_benefit_procedure_udi",
        blank=True,
    )


class ExplanationOfBenefitInsurance(TimeStampedModel):
    """Explanation of Benefit insurance model."""

    focal = models.BooleanField(default=False)
    coverage = models.ForeignKey(
        "coverages.CoverageReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_insurance_coverage",
        null=True,
    )
    pre_auth_ref = ArrayField(models.CharField(max_length=255), null=True)


class ExplanationOfBenefitAccident(TimeStampedModel):
    """Explanation of Benefit accident model."""

    date = models.DateField(null=True)
    type = models.ForeignKey(
        CodeableConcept,
        related_name="explanation_of_benefit_accident_type",
        on_delete=models.CASCADE,
        null=True,
    )
    location_address = models.ForeignKey(
        Address,
        related_name="explanation_of_benefit_accident_location_address",
        on_delete=models.CASCADE,
        null=True,
    )
    location_reference = models.ForeignKey(
        "locations.LocationReference",
        related_name="explanation_of_benefit_accident_location_location",
        on_delete=models.CASCADE,
        null=True,
    )


class ExplanationOfBenefitItemRequestReference(BaseReference):
    """Explanation of Benefit item request reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_request_reference_identifier",
        null=True,
    )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_request_reference_device_request",
        null=True,
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_request_reference_medication_request",
        null=True,
    )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_request_reference_nutrition_order",
        null=True,
    )

    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_request_reference_service_request",
        null=True,
    )
    supply_request = models.ForeignKey(
        "supplyrequests.SupplyRequest",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_request_reference_supply_request",
        null=True,
    )
    vision_prescription = models.ForeignKey(
        "visionprescriptions.VisionPrescription",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_request_reference_vision_prescription",
        null=True,
    )


class ExplanationOfBenefitItemBodySite(TimeStampedModel):
    """Explanation of Benefit item body site model."""

    site = models.ManyToManyField(
        "bodystructures.BodyStructureCodeableReference",
        related_name="explanation_of_benefit_item_body_site_site",
        blank=True,
    )
    sub_site = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_item_body_site_sub_site",
        blank=True,
    )


class ExplanationOfBenefitItemReviewOutcome(TimeStampedModel):
    """Explanation of Benefit item review outcome model."""

    decision = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_review_outcome_decision",
        null=True,
    )
    reason = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_item_review_outcome_reason",
        blank=True,
    )
    pre_auth_ref = models.CharField(max_length=255)
    pre_auth_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_review_outcome_pre_auth_period",
        null=True,
    )


class ExplanationOfBenefitItemAdjudication(TimeStampedModel):
    """Explanation of Benefit item adjudication model."""

    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_adjudication_category",
        null=True,
    )
    reason = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_adjudication_reason",
        null=True,
    )
    amount = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_adjudication_amount",
        null=True,
    )
    quantity = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_adjudication_quantity",
        null=True,
    )


class ExplanationOfBenefitItemDetailSubDetail(TimeStampedModel):
    """Explanation of Benefit item detail sub detail model."""

    sequence = models.PositiveIntegerField()
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="explanation_of_benefit_item_detail_sub_detail_trace_number",
        blank=True,
    )

    revenue = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_sub_detail_revenue",
        null=True,
    )
    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_sub_detail_category",
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_sub_detail_product_or_service",
        null=True,
    )
    product_or_service_end = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_sub_detail_product_or_service_end",
        null=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_item_detail_sub_detail_modifier",
        blank=True,
    )
    program_code = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_item_detail_sub_detail_program_code",
        blank=True,
    )
    patient_paid = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_sub_detail_patient_paid",
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_sub_detail_quantity",
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_sub_detail_unit_price",
        null=True,
    )
    factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_sub_detail_tax",
        null=True,
    )
    net = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_sub_detail_net",
        null=True,
    )
    udi = models.ManyToManyField(
        "devices.DeviceReference",
        related_name="explanation_of_benefit_item_detail_sub_detail_udi",
        blank=True,
    )
    note_number = ArrayField(
        models.PositiveIntegerField(),
        null=True,
    )
    review_outcome = models.ForeignKey(
        ExplanationOfBenefitItemReviewOutcome,
        related_name="explanation_of_benefit_item_detail_sub_detail_review_outcome",
        on_delete=models.CASCADE,
        null=True,
    )
    adjudication = models.ManyToManyField(
        ExplanationOfBenefitItemAdjudication,
        related_name="explanation_of_benefit_item_detail_sub_detail_adjudication",
        blank=True,
    )


class ExplanationOfBenefitItemDetail(TimeStampedModel):
    """Explanation of Benefit item detail model."""

    sequence = models.PositiveIntegerField()
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="explanation_of_benefit_item_detail_trace_number",
        blank=True,
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_revenue",
        null=True,
    )
    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_category",
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_product_or_service",
        null=True,
    )
    product_or_service_end = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_product_or_service_end",
        null=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_item_detail_modifier",
        blank=True,
    )
    program_code = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_item_detail_program_code",
        blank=True,
    )
    patient_paid = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_patient_paid",
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_quantity",
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_unit_price",
        null=True,
    )
    factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_tax",
        null=True,
    )
    net = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_item_detail_net",
        null=True,
    )
    udi = models.ManyToManyField(
        "devices.DeviceReference",
        related_name="explanation_of_benefit_item_detail_udi",
        blank=True,
    )
    note_number = ArrayField(
        models.PositiveIntegerField(),
        null=True,
    )
    review_outcome = models.ForeignKey(
        ExplanationOfBenefitItemReviewOutcome,
        related_name="explanation_of_benefit_item_detail_review_outcome",
        on_delete=models.CASCADE,
        null=True,
    )
    adjudication = models.ManyToManyField(
        ExplanationOfBenefitItemAdjudication,
        related_name="explanation_of_benefit_item_detail_adjudication",
        blank=True,
    )
    sub_detail = models.ManyToManyField(
        ExplanationOfBenefitItemDetailSubDetail,
        related_name="explanation_of_benefit_item_detail_sub_detail",
        blank=True,
    )


class ExplanationOfBenefitItem(TimeStampedModel):
    """Explanation of benefit item."""

    sequence = models.PositiveIntegerField()
    care_team_sequence = ArrayField(models.PositiveIntegerField(), null=True)
    diagnosis_sequence = ArrayField(models.PositiveIntegerField(), null=True)
    procedure_sequence = ArrayField(models.PositiveIntegerField(), null=True)
    information_sequence = ArrayField(models.PositiveIntegerField(), null=True)
    trace_number = models.ManyToManyField(
        Identifier, related_name="explanation_of_benefit_item_trace_number", blank=True
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        related_name="explanation_of_benefit_item_revenue",
        on_delete=models.CASCADE,
        null=True,
    )
    category = models.ForeignKey(
        CodeableConcept,
        related_name="explanation_of_benefit_item_category",
        on_delete=models.CASCADE,
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        related_name="explanation_of_benefit_item_product_or_service",
        on_delete=models.CASCADE,
        null=True,
    )
    product_or_service_end = models.ForeignKey(
        CodeableConcept,
        related_name="explanation_of_benefit_item_product_or_service_end",
        on_delete=models.CASCADE,
        null=True,
    )
    request = models.ManyToManyField(
        ExplanationOfBenefitItemRequestReference,
        related_name="explanation_of_benefit_item_request",
        blank=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept, related_name="explanation_of_benefit_item_modifier", blank=True
    )
    program_code = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_item_program_code",
        blank=True,
    )
    serviced_date = models.DateField(null=True)
    serviced_period = models.ForeignKey(
        Period,
        related_name="explanation_of_benefit_item_serviced_period",
        on_delete=models.CASCADE,
        null=True,
    )
    location_codeable_concept = models.ForeignKey(
        CodeableConcept,
        related_name="explanation_of_benefit_item_location_codeable_concept",
        on_delete=models.CASCADE,
        null=True,
    )
    location_address = models.ForeignKey(
        Address,
        related_name="explanation_of_benefit_item_location_address",
        on_delete=models.CASCADE,
        null=True,
    )
    location_reference = models.ForeignKey(
        "locations.LocationReference",
        related_name="explanation_of_benefit_item_location_reference",
        on_delete=models.CASCADE,
        null=True,
    )
    patient_paid = models.ForeignKey(
        Money,
        related_name="explanation_of_benefit_item_patient_paid",
        on_delete=models.CASCADE,
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        related_name="explanation_of_benefit_item_quantity",
        on_delete=models.CASCADE,
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        related_name="explanation_of_benefit_item_unit_price",
        on_delete=models.CASCADE,
        null=True,
    )
    factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.ForeignKey(
        Money,
        related_name="explanation_of_benefit_item_tax",
        on_delete=models.CASCADE,
        null=True,
    )
    net = models.ForeignKey(
        Money,
        related_name="explanation_of_benefit_item_net",
        on_delete=models.CASCADE,
        null=True,
    )
    udi = models.ManyToManyField(
        "devices.DeviceReference",
        related_name="explanation_of_benefit_item_udi",
        blank=True,
    )
    body_site = models.ManyToManyField(
        ExplanationOfBenefitItemBodySite,
        related_name="explanation_of_benefit_item_body_site",
        blank=True,
    )
    encounter = models.ManyToManyField(
        "encounters.EncounterReference",
        related_name="explanation_of_benefit_item_encounter",
        blank=True,
    )
    note_number = ArrayField(
        models.PositiveIntegerField(),
        null=True,
    )
    review_outcome = models.ForeignKey(
        ExplanationOfBenefitItemReviewOutcome,
        related_name="explanation_of_benefit_item_review_outcome",
        on_delete=models.CASCADE,
        null=True,
    )
    adjudication = models.ManyToManyField(
        ExplanationOfBenefitItemAdjudication,
        related_name="explanation_of_benefit_item_adjudication",
        blank=True,
    )
    detail = models.ManyToManyField(
        ExplanationOfBenefitItemDetail,
        related_name="explanation_of_benefit_item_detail",
        blank=True,
    )


class ExplanationOfBenefitAddItemDetailSubDetail(TimeStampedModel):
    """Explanation of Benefit add item detail sub detail model."""

    trace_number = models.ManyToManyField(
        Identifier,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_trace_number",
        blank=True,
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_revenue",
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_product_or_service",
        null=True,
    )
    product_or_service_end = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_product_or_service_end",
        null=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_modifier",
        blank=True,
    )
    patient_paid = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_patient_paid",
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_quantity",
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_unit_price",
        null=True,
    )
    factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_tax",
        null=True,
    )
    net = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_net",
        null=True,
    )
    note_number = ArrayField(
        models.PositiveIntegerField(),
        null=True,
    )
    review_outcome = models.ForeignKey(
        ExplanationOfBenefitItemReviewOutcome,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_review_outcome",
        null=True,
    )
    adjudication = models.ManyToManyField(
        ExplanationOfBenefitItemAdjudication,
        related_name="explanation_of_benefit_add_item_detail_sub_detail_adjudication",
        blank=True,
    )


class ExplanationOfBenefitAddItemDetail(TimeStampedModel):
    """Explanation of Benefit add item detail model."""

    trace_number = models.ManyToManyField(
        Identifier,
        related_name="explanation_of_benefit_add_item_detail_trace_number",
        blank=True,
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_revenue",
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_product_or_service",
        null=True,
    )
    product_or_service_end = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_product_or_service_end",
        null=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_add_item_detail_modifier",
        blank=True,
    )
    patient_paid = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_patient_paid",
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_quantity",
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_unit_price",
        null=True,
    )
    factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_tax",
        null=True,
    )
    net = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_net",
        null=True,
    )
    note_number = ArrayField(
        models.PositiveIntegerField(),
        null=True,
    )
    review_outcome = models.ForeignKey(
        ExplanationOfBenefitItemReviewOutcome,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_detail_review_outcome",
        null=True,
    )
    adjudication = models.ManyToManyField(
        ExplanationOfBenefitItemAdjudication,
        related_name="explanation_of_benefit_add_item_detail_adjudication",
        blank=True,
    )
    sub_detail = models.ManyToManyField(
        ExplanationOfBenefitAddItemDetailSubDetail,
        related_name="explanation_of_benefit_add_item_detail_sub_detail",
        blank=True,
    )


class ExplanationOfBenefitAddItem(TimeStampedModel):
    """Explanation of Benefit add item model."""

    item_sequence = ArrayField(models.PositiveIntegerField(), null=True)
    detail_sequence = ArrayField(models.PositiveIntegerField(), null=True)
    sub_detail_sequence = ArrayField(models.PositiveIntegerField(), null=True)
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="explanation_of_benefit_add_item_trace_number",
        blank=True,
    )
    provider = models.ManyToManyField(
        ExplanationOfBenefitProviderReference,
        related_name="explanation_of_benefit_add_item_provider",
        blank=True,
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_revenue",
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_product_or_service",
        null=True,
    )
    product_or_service_end = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_product_or_service_end",
        null=True,
    )
    request = models.ManyToManyField(
        ExplanationOfBenefitItemRequestReference,
        related_name="explanation_of_benefit_add_item_request",
        blank=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_add_item_modifier",
        blank=True,
    )
    program_code = models.ManyToManyField(
        CodeableConcept,
        related_name="explanation_of_benefit_add_item_program_code",
        blank=True,
    )
    serviced_date = models.DateField(null=True)
    serviced_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_serviced_period",
        null=True,
    )
    location_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_location_codeable_concept",
        null=True,
    )
    location_address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_location_address",
        null=True,
    )
    location_reference = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_location_reference",
        null=True,
    )
    patient_paid = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_patient_paid",
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_quantity",
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_unit_price",
        null=True,
    )
    factor = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    tax = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_tax",
        null=True,
    )
    net = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_net",
        null=True,
    )
    body_site = models.ManyToManyField(
        ExplanationOfBenefitItemBodySite,
        related_name="explanation_of_benefit_add_item_body_site",
        blank=True,
    )
    note_number = ArrayField(
        models.PositiveIntegerField(),
        null=True,
    )
    review_outcome = models.ForeignKey(
        ExplanationOfBenefitItemReviewOutcome,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_add_item_review_outcome",
        null=True,
    )
    adjudication = models.ManyToManyField(
        ExplanationOfBenefitItemAdjudication,
        related_name="explanation_of_benefit_add_item_adjudication",
        blank=True,
    )
    detail = models.ManyToManyField(
        ExplanationOfBenefitAddItemDetail,
        related_name="explanation_of_benefit_add_item_detail",
        blank=True,
    )


class ExplanationOfBenefitTotal(TimeStampedModel):
    """Explanation of Benefit total model."""

    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_total_category",
        null=True,
    )
    amount = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_total_amount",
        null=True,
    )


class ExplanationOfBenefitPayment(TimeStampedModel):
    """Explanation of Benefit payment model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payment_type",
        null=True,
    )
    adjustment = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payment_adjustment",
        null=True,
    )
    adjustment_reason = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payment_adjustment_reason",
        null=True,
    )
    date = models.DateField()
    amount = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payment_amount",
        null=True,
    )
    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_payment_identifier",
        null=True,
    )


class ExplanationOfBenefitProcessNote(TimeStampedModel):
    """Explanation of Benefit process note model."""

    number = models.PositiveIntegerField()
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_process_note_type",
        null=True,
    )
    text = models.TextField()
    language = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_process_note_language",
        null=True,
    )


class ExplanationOfBenefitBenefitBalanceFinancial(TimeStampedModel):
    """Explanation of Benefit benefit balance financial model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_benefit_balance_financial_type",
        null=True,
    )
    allowed_unsigned_int = models.PositiveIntegerField(null=True)
    allowed_string = models.CharField(max_length=255, null=True)
    allowed_money = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_benefit_balance_financial_allowed_money",
        null=True,
    )
    used_unsigned_int = models.PositiveIntegerField(null=True)
    used_money = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_benefit_balance_financial_used_money",
        null=True,
    )


class ExplanationOfBenefitBenefitBalance(TimeStampedModel):
    """Explanation of Benefit benefit balance model."""

    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_benefit_balance_category",
        null=True,
    )
    excluded = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True)
    description = models.TextField()
    network = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_benefit_balance_network",
        null=True,
    )
    unit = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_benefit_balance_unit",
        null=True,
    )
    term = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefit_benefit_balance_term",
        null=True,
    )
    financial = models.ManyToManyField(
        ExplanationOfBenefitBenefitBalanceFinancial,
        related_name="explanation_of_benefit_benefit_balance_financial",
        blank=True,
    )


class ExplanationOfBenefit(TimeStampedModel):
    """Explanation of Benefits model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="explanation_of_benefits_identifier",
        blank=True,
    )
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="explanation_of_benefits_trace_number",
        blank=True,
    )
    status = models.CharField(
        max_length=255,
        choices=choices.ExplanationOfBenefitStatus.choices,
        default=choices.ExplanationOfBenefitStatus.ACTIVE,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_type",
        null=True,
    )
    sub_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_sub_type",
        null=True,
    )
    use = models.CharField(
        max_length=255,
        choices=choices.ExplanationOfBenefitUse.choices,
        default=choices.ExplanationOfBenefitUse.CLAIM,
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_patient",
        null=True,
    )
    billable_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_billable_period",
        null=True,
    )
    created = models.DateTimeField()
    enterer = models.ForeignKey(
        ExplanationOfBenefitEntererReference,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_enterer",
        null=True,
    )
    insurer = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_insurer",
        null=True,
    )
    provider = models.ForeignKey(
        ExplanationOfBenefitProviderReference,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_provider",
        null=True,
    )
    priority = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_priority",
        null=True,
    )
    funds_reserve_requested = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_funds_reserve_requested",
        null=True,
    )
    funds_reserve = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_funds_reserve",
        null=True,
    )
    related = models.ManyToManyField(
        ExplanationOfBenefitRelated,
        related_name="explanation_of_benefits_funds_related",
        blank=True,
    )
    prescription = models.ForeignKey(
        ExplanationOfBenefitPrescriptionReference,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_prescription",
        null=True,
    )
    original_prescription = models.ForeignKey(
        "medicationrequests.MedicationRequestReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_original_prescription",
        null=True,
    )
    event = models.ManyToManyField(
        ExplanationOfBenefitEvent,
        related_name="explanation_of_benefits_event",
        blank=True,
    )
    payee = models.ForeignKey(
        ExplanationOfBenefitPayee,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_payee",
        null=True,
    )
    referral = models.ForeignKey(
        "servicerequests.ServiceRequestReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_referral",
        null=True,
    )
    encounter = models.ManyToManyField(
        "encounters.EncounterReference",
        related_name="explanation_of_benefits_encounter",
        blank=True,
    )
    facility = models.ForeignKey(
        "locations.LocationOrganizationReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_facility",
        null=True,
    )
    claim = models.ForeignKey(
        "claims.ClaimReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_claim",
        null=True,
    )
    claim_response = models.ForeignKey(
        "claimresponses.ClaimResponseReference",
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_claim_response",
        null=True,
    )
    outcome = models.CharField(
        max_length=255,
        choices=choices.ExplanationOfBenefitOutcome.choices,
        default=choices.ExplanationOfBenefitOutcome.COMPLETE,
    )
    decision = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_decision",
        null=True,
    )
    disposition = models.TextField(null=True)
    pre_auth_ref = ArrayField(models.CharField(max_length=255), null=True)
    pre_auth_period = models.ManyToManyField(
        Period,
        related_name="explanation_of_benefits_pre_auth_period",
        blank=True,
    )
    diagnosis_related_group = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="explanation_of_benefits_diagnosis_related_group",
        null=True,
    )
    care_team = models.ManyToManyField(
        ExplanationOfBenefitCareTeam,
        related_name="explanation_of_benefits_care_team",
        blank=True,
    )
    supporting_info = models.ManyToManyField(
        ExplanationOfBenefitSupportingInfo,
        related_name="explanation_of_benefits_supporting_info",
        blank=True,
    )
    diagnosis = models.ManyToManyField(
        ExplanationOfBenefitDiagnosis,
        related_name="explanation_of_benefits_diagnosis",
        blank=True,
    )
    procedure = models.ManyToManyField(
        ExplanationOfBenefitProcedure,
        related_name="explanation_of_benefits_procedure",
        blank=True,
    )
    precedence = models.PositiveIntegerField(null=True)
    insurance = models.ManyToManyField(
        ExplanationOfBenefitInsurance,
        related_name="explanation_of_benefits_insurance",
        blank=True,
    )
    accident = models.ForeignKey(
        ExplanationOfBenefitAccident,
        related_name="explanation_of_benefits_accident",
        on_delete=models.CASCADE,
        null=True,
    )
    patient_paid = models.ForeignKey(
        Money,
        related_name="explanation_of_benefits_patient_paid",
        on_delete=models.CASCADE,
        null=True,
    )
    item = models.ManyToManyField(
        ExplanationOfBenefitItem,
        related_name="explanation_of_benefits_item",
        blank=True,
    )
    add_item = models.ManyToManyField(
        ExplanationOfBenefitAddItem,
        related_name="explanation_of_benefits_add_item",
        blank=True,
    )
    adjudication = models.ManyToManyField(
        ExplanationOfBenefitItemAdjudication,
        related_name="explanation_of_benefits_adjudication",
        blank=True,
    )
    total = models.ManyToManyField(
        ExplanationOfBenefitTotal,
        related_name="explanation_of_benefits_total",
        blank=True,
    )
    payment = models.ForeignKey(
        ExplanationOfBenefitPayment,
        related_name="explanation_of_benefits_payment",
        on_delete=models.CASCADE,
        null=True,
    )
    form_code = models.ForeignKey(
        CodeableConcept,
        related_name="explanation_of_benefits_form_code",
        on_delete=models.CASCADE,
        null=True,
    )
    form = models.ForeignKey(
        Attachment,
        related_name="explanation_of_benefits_form",
        on_delete=models.CASCADE,
        null=True,
    )
    process_note = models.ManyToManyField(
        ExplanationOfBenefitProcessNote,
        related_name="explanation_of_benefits_process_note",
        blank=True,
    )
    benefit_period = models.ForeignKey(
        Period,
        related_name="explanation_of_benefits_benefit_period",
        on_delete=models.CASCADE,
        null=True,
    )
    benefit_balance = models.ManyToManyField(
        ExplanationOfBenefitBenefitBalance,
        related_name="explanation_of_benefits_benefit_balance",
        blank=True,
    )
