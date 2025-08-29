"""Account Serializers."""

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
from dfhir.conditions.serializers import ConditionCodeableReferenceSerializer
from dfhir.coverages.serializers import CoverageReferenceSerializer
from dfhir.devices.serializers import DeviceReferenceSerializer
from dfhir.encounters.serializers import EncounterEpisodeOfCareReferenceSerializer
from dfhir.procedures.serializers import ProcedureCodeableReferenceSerializer

from .models import (
    Account,
    AccountBalance,
    AccountCoverage,
    AccountDiagnosis,
    AccountGuarantor,
    AccountProcedure,
    AccountReference,
    AccountRelatedAccount,
    AccountsGuarantorPartyReference,
    AccountSubjectReference,
)


class AccountReferenceSerializer(BaseReferenceModelSerializer):
    """Account reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AccountReference
        exclude = ["created_at", "updated_at"]


class AccountDiagnosisSerializer(WritableNestedModelSerializer):
    """Account diagnosis serializer."""

    condition = ConditionCodeableReferenceSerializer(required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    package_code = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = AccountDiagnosis
        exclude = ["created_at", "updated_at"]


class AccountGuarantorPartyReferenceSerializer(BaseReferenceModelSerializer):
    """Account guarantor party reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AccountsGuarantorPartyReference
        exclude = ["created_at", "updated_at"]


class AccountGuarantorSerializer(WritableNestedModelSerializer):
    """Account guarantor serializer."""

    party = AccountGuarantorPartyReferenceSerializer(required=False)
    period = PeriodSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AccountGuarantor
        exclude = ["created_at", "updated_at"]


class AccountBalanceSerializer(WritableNestedModelSerializer):
    """Account balance serializer."""

    aggregate = CodeableConceptSerializer(required=False)
    term = CodeableConceptSerializer(required=False)
    amount = MoneySerializer(required=False)

    class Meta:
        """Meta class."""

        model = AccountBalance
        exclude = ["created_at", "updated_at"]


class AccountCoverageSerializer(WritableNestedModelSerializer):
    """Account coverage serializer."""

    coverage = CoverageReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AccountCoverage
        exclude = ["created_at", "updated_at"]


class AccountProcedureSerializer(WritableNestedModelSerializer):
    """Account procedure serializer."""

    code = ProcedureCodeableReferenceSerializer(required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    package_code = CodeableConceptSerializer(many=True, required=False)
    device = DeviceReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = AccountProcedure
        exclude = ["created_at", "updated_at"]


class AccountRelatedAccountSerializer(WritableNestedModelSerializer):
    """Account related account serializer."""

    relationship = CodeableConceptSerializer(required=False)
    account = AccountReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AccountRelatedAccount
        exclude = ["created_at", "updated_at"]


class AccountSubjectReferenceSerializer(WritableNestedModelSerializer):
    """Account subject reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AccountSubjectReference
        exclude = ["created_at", "updated_at"]


class AccountSerializer(BaseWritableNestedModelSerializer):
    """Account serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    billing_status = CodeableConceptSerializer(required=False)
    type = CodeableConceptSerializer(required=False)
    subject = AccountSubjectReferenceSerializer(many=True, required=False)
    service_period = PeriodSerializer(required=False)
    covers = EncounterEpisodeOfCareReferenceSerializer(many=True, required=False)
    coverage = AccountCoverageSerializer(many=True, required=False)
    owner = OrganizationReferenceSerializer(required=False)
    guarantor = AccountGuarantorSerializer(many=True, required=False)
    diagnosis = AccountDiagnosisSerializer(many=True, required=False)
    procedure = AccountProcedureSerializer(many=True, required=False)
    related_account = AccountRelatedAccountSerializer(many=True, required=False)
    currency = CodeableConceptSerializer(required=False)
    balance = AccountBalanceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Account
        exclude = ["created_at", "updated_at"]
