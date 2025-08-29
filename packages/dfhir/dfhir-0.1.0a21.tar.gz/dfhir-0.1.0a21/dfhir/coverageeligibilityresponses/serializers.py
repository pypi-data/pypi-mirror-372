"""CoverageEligibilityResponse serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    MoneySerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
)
from dfhir.coverages.serializers import CoverageReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)

from .models import (
    CoverageEligibilityResponse,
    CoverageEligibilityResponseError,
    CoverageEligibilityResponseEvent,
    CoverageEligibilityResponseInsurance,
    CoverageEligibilityResponseInsuranceItem,
    CoverageEligibilityResponseInsuranceItemBenefit,
    CoverageEligibilityResponseRequesterReference,
)


class CoverageEligibilityResponseErrorSerializer(WritableNestedModelSerializer):
    """Coverage Eligibility Response Error serializer."""

    code = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityResponseError
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityResponseInsuranceItemBenefitSerializer(
    WritableNestedModelSerializer
):
    """Coverage Eligibility Response Insurance Item Benefit serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    allowed_money = MoneySerializer(many=False, required=False)
    used_money = MoneySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityResponseInsuranceItemBenefit
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityResponseInsuranceItemSerializer(WritableNestedModelSerializer):
    """Coverage Eligibility Response Insurance Item serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    modifier = CodeableConceptSerializer(many=True, required=False)
    provider = PractitionerPractitionerRoleReferenceSerializer(
        many=False, required=False
    )
    network = CodeableConceptSerializer(many=False, required=False)
    unit = CodeableConceptSerializer(many=False, required=False)
    term = CodeableConceptSerializer(many=False, required=False)
    benefit = CoverageEligibilityResponseInsuranceItemBenefitSerializer(
        many=True, required=False
    )
    authorization_supporting = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityResponseInsuranceItem
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityResponseInsuranceSerializer(WritableNestedModelSerializer):
    """Coverage Eligibility Response Insurance serializer."""

    coverage = CoverageReferenceSerializer(many=False, required=False)
    benefit_period = PeriodSerializer(many=False, required=False)
    item = CoverageEligibilityResponseInsuranceItemSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityResponseInsurance
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityResponseEventSerializer(WritableNestedModelSerializer):
    """Coverage Eligibility Response Event serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    when_period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityResponseEvent
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityResponseRequesterReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Coverage Eligibility Response Requester Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityResponseRequesterReference
        exclude = ["created_at", "updated_at"]


class CoverageEligibilityResponseSerializer(BaseWritableNestedModelSerializer):
    """Coverage Eligibility Response serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)
    event = CoverageEligibilityResponseEventSerializer(many=True, required=False)
    serviced_period = PeriodSerializer(many=False, required=False)
    requestor = CoverageEligibilityResponseRequesterReferenceSerializer(  # codespell:ignore requestor
        many=False, required=False
    )
    insurer = OrganizationReferenceSerializer(many=False, required=False)
    insurance = CoverageEligibilityResponseInsuranceSerializer(
        many=True, required=False
    )
    form = CodeableConceptSerializer(many=False, required=False)
    error = CoverageEligibilityResponseErrorSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = CoverageEligibilityResponse
        exclude = ["created_at", "updated_at"]
