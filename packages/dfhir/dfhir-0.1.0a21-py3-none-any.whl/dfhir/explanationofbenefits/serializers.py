"""Explanation of Benefits serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AddressSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodingSerializer,
    IdentifierSerializer,
    MoneySerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    QuantitySerializer,
    ReferenceSerializer,
    SimpleQuantitySerializer,
)
from dfhir.bodystructures.serializers import BodyStructureCodeableReferenceSerializer
from dfhir.claimresponses.serializers import ClaimResponseReferenceSerializer
from dfhir.claims.serializers import ClaimReferenceSerializer
from dfhir.conditions.serializers import ConditionReferenceSerializer
from dfhir.coverages.serializers import CoverageReferenceSerializer
from dfhir.devices.serializers import DeviceReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import (
    LocationOrganizationReferenceSerializer,
    LocationReferenceSerializer,
)
from dfhir.patients.serializers import PatientReferenceSerializer
from dfhir.procedures.serializers import ProcedureReferenceSerializer
from dfhir.servicerequests.serializers import ServiceRequestReferenceSerializer

from .models import (
    ExplanationOfBenefit,
    ExplanationOfBenefitAccident,
    ExplanationOfBenefitAddItem,
    ExplanationOfBenefitAddItemDetail,
    ExplanationOfBenefitBenefitBalance,
    ExplanationOfBenefitBenefitBalanceFinancial,
    ExplanationOfBenefitCareTeam,
    ExplanationOfBenefitDiagnosis,
    ExplanationOfBenefitEntererReference,
    ExplanationOfBenefitEvent,
    ExplanationOfBenefitInsurance,
    ExplanationOfBenefitItem,
    ExplanationOfBenefitItemAdjudication,
    ExplanationOfBenefitItemBodySite,
    ExplanationOfBenefitItemDetail,
    ExplanationOfBenefitItemDetailSubDetail,
    ExplanationOfBenefitItemRequestReference,
    ExplanationOfBenefitItemReviewOutcome,
    ExplanationOfBenefitPayee,
    ExplanationOfBenefitPayeePartyReference,
    ExplanationOfBenefitPayment,
    ExplanationOfBenefitPrescriptionReference,
    ExplanationOfBenefitProcedure,
    ExplanationOfBenefitProcessNote,
    ExplanationOfBenefitProviderReference,
    ExplanationOfBenefitRelated,
    ExplanationOfBenefitSupportingInfo,
    ExplanationOfBenefitTotal,
)


class ExplanationOfBenefitPrescriptionReferenceSerializer(BaseReferenceModelSerializer):
    """Explanation of Benefit Prescription Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitPrescriptionReference
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitProviderReferenceSerializer(BaseReferenceModelSerializer):
    """Explanation of Benefit Provider Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitProviderReference
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitItemRequestReferenceSerializer(BaseReferenceModelSerializer):
    """Explanation of Benefit Item Request Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitItemRequestReference
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitsRelatedSerializer(WritableNestedModelSerializer):
    """Explanation of Benefits Related Serializer."""

    claim = ClaimReferenceSerializer(many=False, required=False)
    relationship = CodeableConceptSerializer(many=False, required=False)
    reference = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitRelated
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitBenefitBalanceFinancialSerializer(
    WritableNestedModelSerializer
):
    """Explanation of Benefit Benefit Balance Financial Serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    allowed_money = MoneySerializer(many=False, required=False)
    used_money = MoneySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitBenefitBalanceFinancial
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitItemBodySiteSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Item Body Site Serializer."""

    site = BodyStructureCodeableReferenceSerializer(many=True, required=False)
    sub_site = CodingSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitItemBodySite
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitItemReviewOutcomeSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Item Review Outcome Serializer."""

    code = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitItemReviewOutcome
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitItemAdjudicationSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Item Adjudication Serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    reason = CodeableConceptSerializer(many=False, required=False)
    amount = MoneySerializer(many=False, required=False)
    quantity = QuantitySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitItemAdjudication
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitItemDetailSubDetailSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Item Detail Sub Detail Serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    revenue = CodeableConceptSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    product_or_service_end = CodeableConceptSerializer(many=False, required=False)
    modifier = CodeableConceptSerializer(many=True, required=False)
    program_code = CodeableConceptSerializer(many=True, required=False)
    patient_paid = MoneySerializer(many=False, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    tax = MoneySerializer(many=False, required=False)
    net = MoneySerializer(many=False, required=False)
    udi = DeviceReferenceSerializer(many=True, required=False)
    review_outcome = ExplanationOfBenefitItemReviewOutcomeSerializer(
        many=False, required=False
    )
    adjudication = ExplanationOfBenefitItemAdjudicationSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitItemDetailSubDetail
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitAddItemDetailSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Add Item Detail Serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    revenue = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    product_or_service_end = CodeableConceptSerializer(many=False, required=False)
    modifier = CodeableConceptSerializer(many=True, required=False)
    patient_paid = MoneySerializer(many=False, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    tax = MoneySerializer(many=False, required=False)
    net = MoneySerializer(many=False, required=False)
    review_outcome = ExplanationOfBenefitItemReviewOutcomeSerializer(
        many=False, required=False
    )
    adjudication = ExplanationOfBenefitItemAdjudicationSerializer(
        many=True, required=False
    )
    sub_detail = ExplanationOfBenefitItemDetailSubDetailSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitAddItemDetail
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitBenefitBalanceSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Benefit Balance Serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    network = CodeableConceptSerializer(many=False, required=False)
    unit = CodeableConceptSerializer(many=False, required=False)
    term = CodeableConceptSerializer(many=False, required=False)
    financial = ExplanationOfBenefitBenefitBalanceFinancialSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitBenefitBalance
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitPayeePartyReferenceSerializer(BaseReferenceModelSerializer):
    """Explanation of Benefit Payee Party Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitPayeePartyReference
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitPayeeSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Payee Serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    party = ExplanationOfBenefitPayeePartyReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitPayee
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitDiagnosisSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Diagnosis Serializer."""

    diagnosis_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    diagnosis_reference = ConditionReferenceSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    on_admission = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitDiagnosis
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitItemDetailSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Item Detail Serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    revenue = CodeableConceptSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    product_or_service_end = CodeableConceptSerializer(many=False, required=False)
    modifier = CodeableConceptSerializer(many=True, required=False)
    program_code = CodeableConceptSerializer(many=True, required=False)
    patient_paid = MoneySerializer(many=False, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    tax = MoneySerializer(many=False, required=False)
    net = MoneySerializer(many=False, required=False)
    udi = DeviceReferenceSerializer(many=True, required=False)
    review_outcome = ExplanationOfBenefitItemReviewOutcomeSerializer(
        many=False, required=False
    )
    adjudication = ExplanationOfBenefitItemAdjudicationSerializer(
        many=True, required=False
    )
    sub_detail = ExplanationOfBenefitItemDetailSubDetailSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitItemDetail
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitItemSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Item Serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    revenue = CodeableConceptSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    product_or_service_end = CodeableConceptSerializer(many=False, required=False)
    request = ExplanationOfBenefitItemRequestReferenceSerializer(
        many=True, required=False
    )
    modifier = CodeableConceptSerializer(many=True, required=False)
    program_code = CodeableConceptSerializer(many=True, required=False)
    serviced_period = PeriodSerializer(many=False, required=False)
    location_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    location_address = AddressSerializer(many=False, required=False)
    location_reference = LocationReferenceSerializer(many=False, required=False)
    patient_paid = MoneySerializer(many=False, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    tax = MoneySerializer(many=False, required=False)
    net = MoneySerializer(many=False, required=False)
    udi = DeviceReferenceSerializer(many=True, required=False)
    body_site = ExplanationOfBenefitItemBodySiteSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=True, required=False)
    review_outcome = ExplanationOfBenefitItemReviewOutcomeSerializer(
        many=False,
        required=False,
    )
    adjudication = ExplanationOfBenefitItemAdjudicationSerializer(
        many=True, required=False
    )
    detail = ExplanationOfBenefitItemDetailSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitItem
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitAccidentSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Accident Serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    location_address = AddressSerializer(many=False, required=False)
    location_reference = LocationReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitAccident
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitInsuranceSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Insurance Serializer."""

    focal = serializers.BooleanField(required=False)
    coverage = CoverageReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitInsurance
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitEventSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Event Serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    when_period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitEvent
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitPaymentSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Payment Serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    adjustment = MoneySerializer(many=False, required=False)
    adjustment_reason = CodeableConceptSerializer(many=False, required=False)
    amount = MoneySerializer(many=False, required=False)
    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitPayment
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitProcedureSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Procedure Serializer."""

    type = CodeableConceptSerializer(many=True, required=False)
    procedure_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    procedure_reference = ProcedureReferenceSerializer(many=False, required=False)
    udi = DeviceReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitProcedure
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitTotalSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Total Serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    amount = MoneySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitTotal
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitAddItemSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Add Item Serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    provider = ExplanationOfBenefitProviderReferenceSerializer(
        many=True, required=False
    )
    revenue = CodeableConceptSerializer(many=False, required=False)
    product_or_Service = CodeableConceptSerializer(many=False, required=False)
    product_or_service_end = CodeableConceptSerializer(many=False, required=False)
    request = ExplanationOfBenefitItemRequestReferenceSerializer(
        many=True, required=False
    )
    modifier = CodeableConceptSerializer(many=True, required=False)
    program_code = CodeableConceptSerializer(many=True, required=False)
    serviced_period = PeriodSerializer(many=False, required=False)
    location_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    location_address = AddressSerializer(many=False, required=False)
    location_reference = LocationReferenceSerializer(many=False, required=False)
    patient_paid = MoneySerializer(many=False, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    tax = MoneySerializer(many=False, required=False)
    net = MoneySerializer(many=False, required=False)
    body_site = ExplanationOfBenefitItemBodySiteSerializer(many=False, required=False)
    review_outcome = ExplanationOfBenefitItemReviewOutcomeSerializer(
        many=False, required=False
    )
    adjudication = ExplanationOfBenefitItemAdjudicationSerializer(
        many=True, required=False
    )
    detail = ExplanationOfBenefitAddItemDetailSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitAddItem
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitCareTeamSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Care Team Serializer."""

    provider = ExplanationOfBenefitProviderReferenceSerializer(
        many=False, required=False
    )
    role = CodeableConceptSerializer(many=False, required=False)
    specialty = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitCareTeam
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitEntererReferenceSerializer(BaseReferenceModelSerializer):
    """Explanation of Benefit Enterer Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitEntererReference
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitProcessNoteSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Process Note Serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    language = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitProcessNote
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitSupportingInfoSerializer(WritableNestedModelSerializer):
    """Explanation of Benefit Supporting Info Serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    timing_period = PeriodSerializer(many=False, required=False)
    value_quantity = QuantitySerializer(many=False, required=False)
    value_attachment = AttachmentSerializer(many=False, required=False)
    value_reference = ReferenceSerializer(many=False, required=False)
    value_identifier = IdentifierSerializer(many=False, required=False)
    reason = CodingSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefitSupportingInfo
        exclude = ["created_at", "updated_at"]


class ExplanationOfBenefitSerializer(BaseWritableNestedModelSerializer):
    """Explanation of Benefits Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    trace_number = IdentifierSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    sub_type = CodeableConceptSerializer(many=False, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)
    billable_period = PeriodSerializer(many=False, required=False)
    enterer = ExplanationOfBenefitEntererReferenceSerializer(many=False, required=False)
    insurer = OrganizationReferenceSerializer(many=False, required=False)
    provider = ExplanationOfBenefitProviderReferenceSerializer(
        many=False, required=False
    )
    priority = CodeableConceptSerializer(many=False, required=False)
    funds_reserve_requested = CodeableConceptSerializer(many=False, required=False)
    funds_reserve = CodeableConceptSerializer(many=False, required=False)
    related = ExplanationOfBenefitsRelatedSerializer(many=True, required=False)
    prescription = ExplanationOfBenefitPrescriptionReferenceSerializer(
        many=False, required=False
    )
    original_prescription = ExplanationOfBenefitPrescriptionReferenceSerializer(
        many=False, required=False
    )
    event = ExplanationOfBenefitEventSerializer(many=True, required=False)
    payee = ExplanationOfBenefitPayeeSerializer(many=False, required=False)
    referral = ServiceRequestReferenceSerializer(many=False, required=False)
    facility = LocationOrganizationReferenceSerializer(many=False, required=False)
    claim = ClaimReferenceSerializer(many=False, required=False)
    claim_response = ClaimResponseReferenceSerializer(required=False)
    decision = CodeableConceptSerializer(many=False, required=False)
    pre_auth_period = PeriodSerializer(many=False, required=False)
    diagnosis_related_group = CodeableConceptSerializer(many=False, required=False)
    care_team = ExplanationOfBenefitCareTeamSerializer(many=True, required=False)
    supporting_info = ExplanationOfBenefitSupportingInfoSerializer(
        many=True, required=False
    )
    diagnosis = ExplanationOfBenefitDiagnosisSerializer(many=True, required=False)
    procedure = ExplanationOfBenefitProcedureSerializer(many=True, required=False)
    insurance = ExplanationOfBenefitInsuranceSerializer(many=True, required=False)
    accident = ExplanationOfBenefitAccidentSerializer(many=False, required=False)
    patient_paid = MoneySerializer(many=False, required=False)
    item = ExplanationOfBenefitItemSerializer(many=True, required=False)
    add_item = ExplanationOfBenefitAddItemSerializer(many=True, required=False)
    adjudication = ExplanationOfBenefitItemAdjudicationSerializer(
        many=True, required=False
    )
    total = ExplanationOfBenefitTotalSerializer(many=True, required=False)
    payment = ExplanationOfBenefitPaymentSerializer(many=False, required=False)
    form_code = CodeableConceptSerializer(many=False, required=False)
    form = AttachmentSerializer(many=False, required=False)
    process_note = ExplanationOfBenefitProcessNoteSerializer(many=True, required=False)
    benefit_period = PeriodSerializer(many=False, required=False)
    benefit_balance = ExplanationOfBenefitBenefitBalanceSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = ExplanationOfBenefit
        exclude = ["created_at", "updated_at"]
