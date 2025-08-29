"""Coverage serializers."""

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
from dfhir.contracts.serializers import ContractReferenceSerializer
from dfhir.patients.serializers import (
    PatientReferenceSerializer,
    PatientRelatedPersonReferenceSerializer,
)

from .models import (
    Coverage,
    CoverageClaimResponseReference,
    CoverageClass,
    CoverageCostToBeneficiary,
    CoverageCostToBeneficiaryException,
    CoveragePaymentBy,
    CoveragePaymentByPartyReference,
    CoveragePolicyHolderReference,
    CoverageReference,
)


class CoveragePolicyHolderReferenceSerializer(BaseReferenceModelSerializer):
    """Policy Holder Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = CoveragePolicyHolderReference
        exclude = ["created_at", "updated_at"]


class CoveragePaymentByPartyReferenceSerializer(BaseReferenceModelSerializer):
    """Coverage By Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = CoveragePaymentByPartyReference
        exclude = ["created_at", "updated_at"]


class CoveragePaymentBySerializer(WritableNestedModelSerializer):
    """Coverage Payment By Serializer."""

    party = CoveragePaymentByPartyReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoveragePaymentBy
        exclude = ["created_at", "updated_at"]


class CoverageCostToBeneficiaryExceptionSerializer(WritableNestedModelSerializer):
    """Coverage Cost To Beneficiary Exception Serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageCostToBeneficiaryException
        exclude = ["created_at", "updated_at"]


class CoverageCostToBeneficiarySerializer(WritableNestedModelSerializer):
    """Coverage Cost To Beneficiary Serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=False, required=False)
    network = CodeableConceptSerializer(many=False, required=False)
    unit = CodeableConceptSerializer(many=False, required=False)
    term = CodeableConceptSerializer(many=False, required=False)
    value_quantity = SimpleQuantitySerializer(many=False, required=False)
    value_money = MoneySerializer(many=False, required=False)
    exception = CoverageCostToBeneficiaryExceptionSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = CoverageCostToBeneficiary
        exclude = ["created_at", "updated_at"]


class CoverageClassSerializer(WritableNestedModelSerializer):
    """Coverage Class Serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    value = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageClass
        exclude = ["created_at", "updated_at"]


class CoverageSerializer(BaseWritableNestedModelSerializer):
    """Coverage Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    payment_by = CoveragePaymentBySerializer(required=False)
    type = CodeableConceptSerializer(required=False)
    policy_holder = CoveragePolicyHolderReferenceSerializer(required=False)
    subscriber = PatientRelatedPersonReferenceSerializer(required=False)
    subscriber_identifier = IdentifierSerializer(required=False, many=True)
    beneficiary = PatientReferenceSerializer(required=False)
    relationship = CodeableConceptSerializer(required=False)
    period = PeriodSerializer(required=False)
    insurer = OrganizationReferenceSerializer(required=False)
    klass = CoverageClassSerializer(required=False, many=True)
    cost_to_beneficiary = CoverageCostToBeneficiarySerializer(required=False, many=True)
    contract = ContractReferenceSerializer(required=False, many=True)

    class Meta:
        """Meta class."""

        model = Coverage
        exclude = ["created_at", "updated_at"]
        rename_fields = {
            "class": "klass",
            "subscriber_id": "subscriber_identifier",
        }


class CoverageReferenceSerializer(BaseReferenceModelSerializer):
    """Coverage reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CoverageReference
        exclude = ["created_at", "updated_at"]


class CoverageClaimResponseReferenceSerializer(BaseReferenceModelSerializer):
    """coverage claim response reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = CoverageClaimResponseReference
        exclude = ["created_at", "updated_at"]
