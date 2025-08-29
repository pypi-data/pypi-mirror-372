"""CoverageEligibilityRequest serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    MoneySerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    SimpleQuantitySerializer,
)
from dfhir.conditions.serializers import ConditionReferenceSerializer
from dfhir.coverages.serializers import CoverageReferenceSerializer
from dfhir.locations.serializers import (
    LocationOrganizationReferenceSerializer,
    LocationReferenceSerializer,
)
from dfhir.patients.serializers import PatientReferenceSerializer
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)

from .models import (
    CoverageEligibilityRequest,
    CoverageEligibilityRequestEvent,
    CoverageEligibilityRequestInsurance,
    CoverageEligibilityRequestItem,
    CoverageEligibilityRequestItemDetailReference,
    CoverageEligibilityRequestItemDiagnosis,
    CoverageEligibilityRequestProviderReference,
    CoverageEligibilityRequestSupportingInfo,
    CoverageEligibilityRequestSupportingInfoInformationReference,
)


class CoverageEligibilityRequestItemDetailReferenceSerializer(
    BaseReferenceModelSerializer
):
    """CoverageEligibilityRequestItemDetailReference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityRequestItemDetailReference
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityRequestProviderReferenceSerializer(
    BaseReferenceModelSerializer
):
    """CoverageEligibilityRequestProviderReference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityRequestProviderReference
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityRequestItemDiagnosisSerializer(WritableNestedModelSerializer):
    """CoverageEligibilityRequestItemDiagnosis serializer."""

    diagnosis_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    diagnosis_reference = ConditionReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityRequestItemDiagnosis
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityRequestSupportingInfoInformationReferenceSerializer(
    BaseReferenceModelSerializer
):
    """CoverageEligibilityRequestSupportingInfoInformationReference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityRequestSupportingInfoInformationReference
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityRequestItemSerializer(WritableNestedModelSerializer):
    """CoverageEligibilityRequestItem serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    modifier = CodeableConceptSerializer(many=True, required=False)
    provider = PractitionerPractitionerRoleReferenceSerializer(
        many=False, required=False
    )
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    facility = LocationOrganizationReferenceSerializer(many=False, required=False)
    diagnosis = CoverageEligibilityRequestItemDiagnosisSerializer(
        many=True, required=False
    )
    detail = CoverageEligibilityRequestItemDetailReferenceSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = CoverageEligibilityRequestItem
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityRequestEventSerializer(WritableNestedModelSerializer):
    """CoverageEligibilityRequestEvent serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    when_period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityRequestEvent
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityRequestInsuranceSerializer(WritableNestedModelSerializer):
    """CoverageEligibilityRequestInsurance serializer."""

    coverage = CoverageReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityRequestInsurance
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityRequestSupportingInfoSerializer(WritableNestedModelSerializer):
    """CoverageEligibilityRequestSupportingInfo serializer."""

    information = (
        CoverageEligibilityRequestSupportingInfoInformationReferenceSerializer(
            many=False, required=False
        )
    )

    class Meta:
        """Meta class."""

        model = CoverageEligibilityRequestSupportingInfo
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityRequestSerializer(BaseWritableNestedModelSerializer):
    """CoverageEligibilityRequest serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    priority = CodeableConceptSerializer(many=False, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)
    event = CoverageEligibilityRequestEventSerializer(many=True, required=False)
    serviced_period = PeriodSerializer(many=False, required=False)
    enterer = PractitionerPractitionerRoleReferenceSerializer(
        many=False, required=False
    )
    provider = CoverageEligibilityRequestProviderReferenceSerializer(
        many=False, required=False
    )
    insurer = OrganizationReferenceSerializer(many=False, required=False)
    facility = LocationReferenceSerializer(many=False, required=False)
    supporting_info = CoverageEligibilityRequestSupportingInfoSerializer(
        many=True, required=False
    )
    insurance = CoverageEligibilityRequestInsuranceSerializer(many=True, required=False)
    item = CoverageEligibilityRequestItemSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityRequest
        exclude = ["created_at", "updated_at"]
