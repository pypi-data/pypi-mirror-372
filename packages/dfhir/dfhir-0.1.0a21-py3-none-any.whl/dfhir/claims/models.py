"""Claims models."""

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
    Reference,
    SimpleQuantity,
    TimeStampedModel,
)

from . import choices


class ClaimEntererReference(BaseReference):
    """Claim Enterer Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_enterer_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="claim_enterer_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="claim_enterer_reference_practitioner_role",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="claim_enterer_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="claim_enterer_reference_related_person",
        null=True,
    )


class ClaimProviderReference(BaseReference):
    """Claim Provider Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_provider_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="claim_provider_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="claim_provider_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="claim_provider_reference_organization",
        null=True,
    )


class ClaimRelated(TimeStampedModel):
    """Claim related model."""

    claim = models.ForeignKey(
        "ClaimReference",
        on_delete=models.CASCADE,
        related_name="claim_related_claim",
        null=True,
    )
    relationship = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_related_relationship",
        null=True,
    )
    reference = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_related_reference",
        null=True,
    )


class ClaimPrescriptionReference(BaseReference):
    """Claim Prescription Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_prescription_reference_identifier",
        null=True,
    )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.CASCADE,
        related_name="claim_prescription_reference_device_request",
        null=True,
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.CASCADE,
        related_name="claim_prescription_reference_medication_request",
        null=True,
    )
    vision_prescription = models.ForeignKey(
        "visionprescriptions.VisionPrescription",
        on_delete=models.CASCADE,
        related_name="claim_prescription_reference_vision_prescription",
        null=True,
    )


class ClaimOriginalPrescriptionReference(BaseReference):
    """Claim Original Prescription Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_original_prescription_reference_identifier",
        null=True,
    )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.CASCADE,
        related_name="claim_original_prescription_reference_device_request",
        null=True,
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.CASCADE,
        related_name="claim_original_prescription_reference_medication_request",
        null=True,
    )
    vision_prescription = models.ForeignKey(
        "visionprescriptions.VisionPrescription",
        on_delete=models.CASCADE,
        related_name="claim_original_prescription_reference_vision_prescription",
        null=True,
    )


class ClaimPayeePartyReference(BaseReference):
    """Claim Payee Party Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_payee_party_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="claim_payee_party_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="claim_payee_party_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="claim_payee_party_reference_organization",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="claim_payee_party_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="claim_payee_party_reference_related_person",
        null=True,
    )


class ClaimPayee(TimeStampedModel):
    """Claim payee model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_payee_type",
        null=True,
    )
    party = models.ForeignKey(
        ClaimPayeePartyReference,
        on_delete=models.CASCADE,
        related_name="claim_payee_party",
        null=True,
    )


class ClaimCareTeamProviderReference(BaseReference):
    """Care Team Provider Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_care_team_provider_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="claim_care_team_provider_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="claim_care_team_provider_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="claim_care_team_provider_reference_organization",
        null=True,
    )


class ClaimCareTeam(TimeStampedModel):
    """Claim care team model."""

    sequence = models.IntegerField(null=True)
    provider = models.ForeignKey(
        ClaimCareTeamProviderReference,
        on_delete=models.CASCADE,
        related_name="claim_care_team_provider",
        null=True,
    )
    responsible = models.BooleanField(default=False)
    role = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_care_team_role",
        null=True,
    )
    specialty = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_care_team_specialty",
        null=True,
    )


class ClaimSupportingInfo(TimeStampedModel):
    """Claim supporting info model."""

    sequence = models.IntegerField(null=True)
    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_supporting_info_category",
        null=True,
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_supporting_info_code",
        null=True,
    )
    timing_date = models.DateField(null=True)
    timing_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="claim_supporting_info_timing_period",
        null=True,
    )
    value_boolean = models.BooleanField(null=True)
    value_string = models.CharField(max_length=255, null=True)
    value_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        related_name="claim_supporting_info_value_quantity",
        null=True,
    )
    value_attachment = models.ForeignKey(
        Attachment,
        on_delete=models.CASCADE,
        related_name="claim_supporting_info_value_attachment",
        null=True,
    )
    value_reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name="claim_supporting_info_value_reference",
        null=True,
    )
    value_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_supporting_info_value_identifier",
        null=True,
    )
    reason = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_supporting_info_reason",
        null=True,
    )


class ClaimDiagnosis(TimeStampedModel):
    """Claim diagnosis model."""

    sequence = models.IntegerField(null=True)
    diagnosis_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_diagnosis_diagnosis_codeable_concept",
        null=True,
    )
    diagnosis_reference = models.ForeignKey(
        Reference,
        on_delete=models.CASCADE,
        related_name="claim_diagnosis_diagnosis_reference",
        null=True,
    )
    type = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_diagnosis_type",
        blank=True,
    )
    on_admission = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_diagnosis_on_admission",
        null=True,
    )


class ClaimProcedure(TimeStampedModel):
    """Claim procedure model."""

    sequence = models.IntegerField(null=True)
    type = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_procedure_type",
        blank=True,
    )
    date = models.DateField(null=True)
    procedure_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_procedure_procedure_codeable_concept",
        null=True,
    )
    procedure_reference = models.ForeignKey(
        "procedures.ProcedureReference",
        on_delete=models.CASCADE,
        related_name="claim_procedure_procedure_reference",
        null=True,
    )
    udi = models.ManyToManyField(
        "devices.DeviceReference",
        related_name="claim_procedure_udi",
        blank=True,
    )


class ClaimInsurance(TimeStampedModel):
    """Claim insurance model."""

    sequence = models.IntegerField(null=True)
    focal = models.BooleanField(default=False)
    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_insurance_identifier",
        null=True,
    )
    coverage = models.ForeignKey(
        "coverages.CoverageReference",
        on_delete=models.CASCADE,
        related_name="claim_insurance_coverage",
        null=True,
    )
    business_arrangement = models.CharField(max_length=255, null=True)
    pre_auth_ref = ArrayField(models.CharField(max_length=255), null=True)
    # claim_response = models.ForeignKey(
    #     "claimresponses.ClaimResponse",
    #     on_delete=models.CASCADE,
    #     related_name="claim_insurance_claim_response",
    #     null=True,
    # )


class ClaimAccident(TimeStampedModel):
    """Claim accident model."""

    date = models.DateField(null=True)
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="claim_accident_type",
        null=True,
    )
    location_address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        related_name="claim_accident_location_address",
        null=True,
    )
    location_reference = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.CASCADE,
        related_name="claim_accident_location_reference",
        null=True,
    )


class ClaimItemRequestReference(BaseReference):
    """Claim Item Request Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="claim_item_request_reference_identifier",
        null=True,
    )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.CASCADE,
        related_name="claim_item_request_reference_device_request",
        null=True,
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.CASCADE,
        related_name="claim_item_request_reference_medication_request",
        null=True,
    )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.CASCADE,
        related_name="claim_item_request_reference_nutrition_order",
        null=True,
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="claim_item_request_reference_service_request",
        null=True,
    )
    supply_request = models.ForeignKey(
        "supplyrequests.SupplyRequest",
        on_delete=models.CASCADE,
        related_name="claim_item_request_reference_supply_request",
        null=True,
    )
    vision_prescription = models.ForeignKey(
        "visionprescriptions.VisionPrescription",
        on_delete=models.CASCADE,
        related_name="claim_item_request_reference_vision_prescription",
        null=True,
    )


class ClaimItemBodySIte(TimeStampedModel):
    """Claim Item Body Site model."""

    site = models.ManyToManyField(
        "bodystructures.BodyStructureCodeableReference",
        related_name="claim_item_body_site",
        blank=True,
    )
    sub_site = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_item_sub_site",
        blank=True,
    )


class ClaimItemDetailSubDetail(TimeStampedModel):
    """Claim item detail sub detail."""

    sequence = models.IntegerField(null=True)
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="claim_item_detail_sub_detail_trace_number",
        blank=True,
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_detail_sub_detail_revenue",
        on_delete=models.CASCADE,
        null=True,
    )
    category = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_detail_sub_detail_category",
        on_delete=models.CASCADE,
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_detail_sub_detail_product_or_service",
        on_delete=models.CASCADE,
        null=True,
    )
    product_or_service_end = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_detail_sub_detail_product_or_service_end",
        on_delete=models.CASCADE,
        null=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_item_detail_sub_detail_modifier",
        blank=True,
    )
    program_code = models.ManyToManyField(
        CodeableConcept,
        related_name="claim_item_detail_sub_detail_program_code",
        blank=True,
    )
    patient_paid = models.ForeignKey(
        Money,
        related_name="claim_item_detail_sub_detail_patient_paid",
        on_delete=models.CASCADE,
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        related_name="claim_item_detail_sub_detail_quantity",
        on_delete=models.CASCADE,
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        related_name="claim_item_detail_sub_detail_unit_price",
        on_delete=models.CASCADE,
        null=True,
    )
    factor = models.FloatField(null=True)
    tax = models.ForeignKey(
        Money,
        related_name="claim_item_detail_sub_detail_tax",
        on_delete=models.CASCADE,
        null=True,
    )
    net = models.ForeignKey(
        Money,
        related_name="claim_item_detail_sub_detail_net",
        on_delete=models.CASCADE,
        null=True,
    )
    udi = models.ManyToManyField(
        "devices.DeviceReference",
        related_name="claim_item_detail_sub_detail_udi",
        blank=True,
    )


class ClaimItemDetail(TimeStampedModel):
    """Claim item detail."""

    sequence = models.IntegerField(null=True)
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="claim_item_detail_trace_number",
        blank=True,
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_detail_revenue",
        on_delete=models.CASCADE,
        null=True,
    )
    category = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_detail_category",
        on_delete=models.CASCADE,
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_detail_product_or_service",
        on_delete=models.CASCADE,
        null=True,
    )
    modifier = models.ManyToManyField(
        CodeableConcept, related_name="claim_item_detail_modifier", blank=True
    )
    program_code = models.ManyToManyField(
        CodeableConcept, related_name="claim_item_detail_program_code", blank=True
    )
    patient_paid = models.ForeignKey(
        Money,
        related_name="claim_item_detail_patient_paid",
        on_delete=models.CASCADE,
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        related_name="claim_item_detail_quantity",
        on_delete=models.CASCADE,
        null=True,
    )
    unit_price = models.ForeignKey(
        Money,
        related_name="claim_item_detail_unit_price",
        on_delete=models.CASCADE,
        null=True,
    )
    factor = models.FloatField(null=True)
    tax = models.ForeignKey(
        Money, related_name="claim_item_detail_tax", on_delete=models.CASCADE, null=True
    )
    net = models.ForeignKey(
        Money, related_name="claim_item_detail_net", on_delete=models.CASCADE, null=True
    )
    udi = models.ManyToManyField(
        "devices.DeviceReference", related_name="claim_item_detail_udi", blank=True
    )
    sub_detail = models.ManyToManyField(
        ClaimItemDetailSubDetail,
        related_name="claim_item_detail_sub_detail",
        blank=True,
    )


class ClaimItem(TimeStampedModel):
    """Claim item model."""

    sequence = models.IntegerField(null=True)
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="claim_item_trace_number",
        blank=True,
    )
    care_team_sequence = ArrayField(
        models.IntegerField(),
        null=True,
    )
    diagnosis_sequence = ArrayField(
        models.IntegerField(),
        null=True,
    )
    procedure_sequence = ArrayField(
        models.IntegerField(),
        null=True,
    )
    information_sequence = ArrayField(
        models.IntegerField(),
        null=True,
    )
    revenue = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_revenue",
        on_delete=models.CASCADE,
        null=True,
    )
    category = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_category",
        on_delete=models.CASCADE,
        null=True,
    )
    product_or_service = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_product_or_service",
        on_delete=models.CASCADE,
        null=True,
    )
    product_or_service_end = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_product_or_service_end",
        on_delete=models.CASCADE,
        null=True,
    )
    request = models.ManyToManyField(
        ClaimItemRequestReference, related_name="claim_item_request", blank=True
    )
    modifier = models.ManyToManyField(
        CodeableConcept, related_name="claim_item_modifier", blank=True
    )
    program_code = models.ManyToManyField(
        CodeableConcept, related_name="claim_item_program_code", blank=True
    )
    serviced_date = models.DateField(null=True)
    serviced_period = models.ForeignKey(
        Period,
        related_name="claim_item_serviced_period",
        on_delete=models.CASCADE,
        null=True,
    )
    location_codeable_concept = models.ForeignKey(
        CodeableConcept,
        related_name="claim_item_location_codeable_concept",
        on_delete=models.CASCADE,
        null=True,
    )
    location_address = models.ForeignKey(
        Address,
        related_name="claim_item_location_address",
        on_delete=models.CASCADE,
        null=True,
    )
    location_reference = models.ForeignKey(
        "locations.LocationReference",
        related_name="claim_item_location_reference",
        on_delete=models.CASCADE,
        null=True,
    )
    patient_paid = models.ForeignKey(
        Money,
        related_name="claim_item_patient_paid",
        on_delete=models.CASCADE,
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        related_name="claim_item_quantity",
        on_delete=models.CASCADE,
        null=True,
    )
    unit_price = models.ForeignKey(
        Money, related_name="claim_item_unit_price", on_delete=models.CASCADE, null=True
    )
    factor = models.FloatField(null=True)
    tax = models.ForeignKey(
        Money, related_name="claim_item_tax", on_delete=models.CASCADE, null=True
    )
    net = models.ForeignKey(
        Money, related_name="claim_item_net", on_delete=models.CASCADE, null=True
    )
    udi = models.ManyToManyField(
        "devices.DeviceReference", related_name="claim_item_udi", blank=True
    )
    body_site = models.ManyToManyField(
        ClaimItemBodySIte, related_name="claim_item_body_site", blank=True
    )
    encounter = models.ManyToManyField(
        "encounters.EncounterReference", related_name="claim_item_encounter", blank=True
    )
    detail = models.ManyToManyField(
        ClaimItemDetail, related_name="claim_item_detail", blank=True
    )


class ClaimEvent(TimeStampedModel):
    """Claim event model."""

    type = models.ForeignKey(
        CodeableConcept,
        related_name="claim_event_type",
        on_delete=models.CASCADE,
        null=True,
    )
    when_date_time = models.DateTimeField(null=True)
    when_period = models.ForeignKey(
        Period,
        related_name="claim_event_when_period",
        on_delete=models.CASCADE,
        null=True,
    )


class Claim(TimeStampedModel):
    """Claim model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="claim_identifier",
        blank=True,
    )
    trace_number = models.ManyToManyField(
        Identifier,
        related_name="claim_trace_number",
        blank=True,
    )
    status = models.CharField(
        max_length=255,
        choices=choices.ClaimStatus.choices,
        default=choices.ClaimStatus.DRAFT,
    )
    type = models.ForeignKey(
        CodeableConcept, related_name="claim_type", on_delete=models.CASCADE, null=True
    )
    sub_type = models.ForeignKey(
        CodeableConcept,
        related_name="claim_sub_type",
        null=True,
        on_delete=models.CASCADE,
    )
    use = models.CharField(
        max_length=255,
        choices=choices.ClaimUseChoices.choices,
        default=choices.ClaimUseChoices.CLAIM,
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        related_name="claim_patient",
        on_delete=models.CASCADE,
        null=True,
    )
    billable_period = models.ForeignKey(
        Period,
        related_name="claim_billable_period",
        on_delete=models.CASCADE,
        null=True,
    )
    created = models.DateTimeField(auto_created=True, null=True)
    enterer = models.ForeignKey(
        ClaimEntererReference,
        related_name="claim_enterer",
        on_delete=models.CASCADE,
        null=True,
    )
    insurer = models.ForeignKey(
        OrganizationReference,
        related_name="claim_insurer",
        on_delete=models.CASCADE,
        null=True,
    )
    provider = models.ForeignKey(
        ClaimProviderReference,
        related_name="claim_provider",
        on_delete=models.CASCADE,
        null=True,
    )
    priority = models.ForeignKey(
        CodeableConcept,
        related_name="claim_priority",
        on_delete=models.CASCADE,
        null=True,
    )
    funds_reserve = models.ForeignKey(
        CodeableConcept,
        related_name="claim_funds_reserve",
        on_delete=models.CASCADE,
        null=True,
    )
    related = models.ManyToManyField(
        ClaimRelated, related_name="claim_related", blank=True
    )
    prescription = models.ForeignKey(
        ClaimPrescriptionReference,
        related_name="claim_prescription",
        on_delete=models.CASCADE,
        null=True,
    )
    original_prescription = models.ForeignKey(
        ClaimOriginalPrescriptionReference,
        related_name="claim_original_prescription",
        on_delete=models.CASCADE,
        null=True,
    )
    payee = models.ForeignKey(
        ClaimPayee, related_name="claim_payee", on_delete=models.CASCADE, null=True
    )
    referral = models.ForeignKey(
        "servicerequests.ServiceRequestReference",
        related_name="claim_referral",
        on_delete=models.CASCADE,
        null=True,
    )
    encounter = models.ManyToManyField(
        "encounters.EncounterReference", related_name="claim_encounter", blank=True
    )
    facility = models.ForeignKey(
        "locations.LocationOrganizationReference",
        related_name="claim_facility",
        on_delete=models.CASCADE,
        null=True,
    )
    diagnosis_related_group = models.ForeignKey(
        CodeableConcept,
        related_name="claim_diagnosis_related_group",
        on_delete=models.CASCADE,
        null=True,
    )
    event = models.ManyToManyField(ClaimEvent, related_name="claim_event", blank=True)
    care_team = models.ManyToManyField(
        ClaimCareTeam, related_name="claim_care_team", blank=True
    )
    supporting_info = models.ManyToManyField(
        ClaimSupportingInfo, related_name="claim_supporting_info", blank=True
    )
    diagnosis = models.ManyToManyField(
        ClaimDiagnosis, related_name="claim_diagnosis", blank=True
    )
    procedure = models.ManyToManyField(
        ClaimProcedure, related_name="claim_procedure", blank=True
    )
    insurance = models.ManyToManyField(
        ClaimInsurance, related_name="claim_insurance", blank=True
    )
    accident = models.ForeignKey(
        ClaimAccident,
        related_name="claim_accident",
        on_delete=models.CASCADE,
        null=True,
    )
    patient_paid = models.ForeignKey(
        Money, related_name="claim_patient_paid", on_delete=models.CASCADE, null=True
    )
    item = models.ManyToManyField(ClaimItem, related_name="claim_item", blank=True)
    total = models.ForeignKey(
        Money, related_name="claim_total", on_delete=models.CASCADE, null=True
    )


class ClaimReference(BaseReference):
    """Claim Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="claim_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    claim = models.ForeignKey(
        Claim, related_name="claim_reference_claim", on_delete=models.CASCADE, null=True
    )
