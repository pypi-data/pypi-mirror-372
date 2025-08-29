"""Claims serializers."""

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AddressSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    MoneySerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    QuantitySerializer,
    ReferenceSerializer,
    SimpleQuantitySerializer,
)
from dfhir.bodystructures.serializers import BodyStructureCodeableReferenceSerializer
from dfhir.coverages.serializers import CoverageReferenceSerializer
from dfhir.devices.serializers import DeviceReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import (
    LocationOrganizationReferenceSerializer,
    LocationReferenceSerializer,
)

# from dfhir.coverages.serializers import CoverageReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer
from dfhir.procedures.serializers import ProcedureReferenceSerializer
from dfhir.servicerequests.serializers import (
    ServiceRequestReferenceSerializer,
)

from .models import (
    Claim,
    ClaimAccident,
    ClaimCareTeam,
    ClaimCareTeamProviderReference,
    ClaimDiagnosis,
    ClaimEntererReference,
    ClaimEvent,
    ClaimInsurance,
    ClaimItem,
    ClaimItemBodySIte,
    ClaimItemDetail,
    ClaimItemDetailSubDetail,
    ClaimItemRequestReference,
    ClaimOriginalPrescriptionReference,
    ClaimPayee,
    ClaimPayeePartyReference,
    ClaimPrescriptionReference,
    ClaimProcedure,
    ClaimProviderReference,
    ClaimReference,
    ClaimRelated,
    ClaimSupportingInfo,
)


class ClaimReferenceSerializer(BaseReferenceModelSerializer):
    """Claim reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimReference
        exclude = ["created_at", "updated_at"]


class ClaimPayeePartyReferenceSerializer(BaseReferenceModelSerializer):
    """Claim Payee Party Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimPayeePartyReference
        exclude = ["created_at", "updated_at"]


class ClaimCareTeamProviderReferenceSerializer(BaseReferenceModelSerializer):
    """Claim Care team provider reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimCareTeamProviderReference
        exclude = ["created_at", "updated_at"]


class ClaimProviderReferenceSerializer(BaseReferenceModelSerializer):
    """Claim provider reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimProviderReference
        exclude = ["created_at", "updated_at"]


class ClaimItemRequestReferenceSerializer(BaseReferenceModelSerializer):
    """Claim item request reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimItemRequestReference
        exclude = ["created_at", "updated_at"]


class ClaimItemDetailSubDetailSerializer(WritableNestedModelSerializer):
    """Claim item detail sub detail serializer."""

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

    class Meta:
        """Meta class."""

        model = ClaimItemDetailSubDetail
        exclude = ["created_at", "updated_at"]


class ClaimPayeeSerializer(WritableNestedModelSerializer):
    """Claim payee serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    party = ClaimPayeePartyReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimPayee
        exclude = ["created_at", "updated_at"]


class ClaimItemDetailSerializer(WritableNestedModelSerializer):
    """Claim item detail serializer."""

    sequence = serializers.IntegerField(required=False)
    trace_number = IdentifierSerializer(many=True, required=False)
    revenue = CodeableConceptSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    modifier = CodeableConceptSerializer(many=True, required=False)
    program_code = CodeableConceptSerializer(many=True, required=False)
    patient_paid = MoneySerializer(many=False, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    tax = MoneySerializer(many=False, required=False)
    net = MoneySerializer(many=False, required=False)
    udi = DeviceReferenceSerializer(many=True, required=False)
    sub_detail = ClaimItemDetailSubDetailSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClaimItemDetail
        exclude = ["created_at", "updated_at"]


class ClaimItemBodySiteSerializer(WritableNestedModelSerializer):
    """Claim item body site serializer."""

    site = BodyStructureCodeableReferenceSerializer(many=True, required=False)
    sub_site = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClaimItemBodySIte
        exclude = ["created_at", "updated_at"]


class ClaimItemSerializer(WritableNestedModelSerializer):
    """Claim item serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    revenue = CodeableConceptSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    product_or_service_end = CodeableConceptSerializer(many=False, required=False)
    request = ClaimItemRequestReferenceSerializer(many=False, required=False)
    modifier = CodeableConceptSerializer(many=True, required=False)
    program_code = CodeableConceptSerializer(many=True, required=False)
    serviced_date = serializers.DateField(required=False)
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
    body_site = ClaimItemBodySiteSerializer(many=True, required=False)
    encounter = EncounterReferenceSerializer(many=True, required=False)
    detail = ClaimItemDetailSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClaimItem
        exclude = ["created_at", "updated_at"]


class ClaimEventSerializer(WritableNestedModelSerializer):
    """Claim event serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    when_period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimEvent
        exclude = ["created_at", "updated_at"]


class ClaimRelatedSerializer(WritableNestedModelSerializer):
    """Claim related serializer."""

    claim = ClaimReferenceSerializer(many=False, required=False)
    relationship = CodeableConceptSerializer(many=False, required=False)
    reference = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimRelated
        exclude = ["created_at", "updated_at"]


class ClaimAccidentSerializer(WritableNestedModelSerializer):
    """Claim accident serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    location_address = AddressSerializer(many=False, required=False)
    location_reference = LocationReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimAccident
        exclude = ["created_at", "updated_at"]


class ClaimInsuranceSerializer(WritableNestedModelSerializer):
    """Claim insurance serializer."""

    identifier = IdentifierSerializer(many=False, required=False)
    coverage = CoverageReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimInsurance
        exclude = ["created_at", "updated_at"]


class ClaimProcedureSerializer(WritableNestedModelSerializer):
    """Claim procedure serializer."""

    type = CodeableConceptSerializer(many=True, required=False)
    procedure_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    procedure_reference = ProcedureReferenceSerializer(many=False, required=False)
    udi = DeviceReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimProcedure
        exclude = ["created_at", "updated_at"]


class ClaimDiagnosisSerializer(WritableNestedModelSerializer):
    """Claim diagnosis serializer."""

    diagnosis_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    diagnosis_reference = ReferenceSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    on_admission = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimDiagnosis
        exclude = ["created_at", "updated_at"]


class ClaimCareTeamSerializer(WritableNestedModelSerializer):
    """Claim care team serializer."""

    provider = ClaimCareTeamProviderReferenceSerializer(many=False, required=False)
    role = CodeableConceptSerializer(many=False, required=False)
    specialty = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimCareTeam
        exclude = ["created_at", "updated_at"]


class ClaimSupportingInfoSerializer(WritableNestedModelSerializer):
    """Claim supporting info serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    timing_period = PeriodSerializer(many=False, required=False)
    value_quantity = QuantitySerializer(many=False, required=False)
    value_attachment = AttachmentSerializer(many=False, required=False)
    value_reference = ReferenceSerializer(many=False, required=False)
    value_identifier = IdentifierSerializer(many=False, required=False)
    reason = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimSupportingInfo
        exclude = ["created_at", "updated_at"]


class ClaimEntererReferenceSerializer(BaseReferenceModelSerializer):
    """Claim enterer reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimEntererReference
        exclude = ["created_at", "updated_at"]


class ClaimPrescriptionReferenceSerializer(BaseReferenceModelSerializer):
    """Claim prescription reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimPrescriptionReference
        exclude = ["created_at", "updated_at"]


class ClaimOriginalPrescriptionReferenceSerializer(BaseReferenceModelSerializer):
    """Claim original prescription reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimOriginalPrescriptionReference
        exclude = ["created_at", "updated_at"]


class ClaimSerializer(BaseWritableNestedModelSerializer):
    """Claim serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    trace_number = IdentifierSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    sub_type = CodeableConceptSerializer(many=False, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)
    billable_period = PeriodSerializer(many=False, required=False)
    enterer = ClaimEntererReferenceSerializer(many=False, required=False)
    insurer = OrganizationReferenceSerializer(many=False, required=False)
    provider = ClaimProviderReferenceSerializer(many=False, required=False)
    priority = CodeableConceptSerializer(many=False, required=False)
    funds_reserve = CodeableConceptSerializer(many=False, required=False)
    related = ClaimRelatedSerializer(many=True, required=False)
    prescription = ClaimPrescriptionReferenceSerializer(many=False, required=False)
    original_prescription = ClaimOriginalPrescriptionReferenceSerializer(
        many=False, required=False
    )
    payee = ClaimPayeeSerializer(many=False, required=False)
    referral = ServiceRequestReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=True, required=False)
    facility = LocationOrganizationReferenceSerializer(many=False, required=False)
    diagnosis_related_group = CodeableConceptSerializer(many=False, required=False)
    event = ClaimEventSerializer(many=True, required=False)
    care_team = ClaimCareTeamSerializer(many=True, required=False)
    supporting_info = ClaimSupportingInfoSerializer(many=True, required=False)
    diagnosis = ClaimDiagnosisSerializer(many=True, required=False)
    procedure = ClaimProcedureSerializer(many=True, required=False)
    insurance = ClaimInsuranceSerializer(many=True, required=False)
    accident = ClaimAccidentSerializer(many=False, required=False)
    patient_paid = MoneySerializer(many=False, required=False)
    item = ClaimItemSerializer(many=True, required=False)
    total = MoneySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Claim
        exclude = ["created_at", "updated_at"]
