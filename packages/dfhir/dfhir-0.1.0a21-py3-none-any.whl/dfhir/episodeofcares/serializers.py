"""Episode of care serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.accounts.serializers import AccountReferenceSerializer
from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
)
from dfhir.careteams.serializers import CareTeamReferenceSerializer
from dfhir.conditions.serializers import ConditionCodeableReferenceSerializer
from dfhir.patients.serializers import PatientGroupReferenceSerializer
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)
from dfhir.servicerequests.serializers import ServiceRequestReferenceSerializer

from .models import (
    EpisodeOfCare,
    EpisodeOfCareDiagnosis,
    EpisodeOfCareReason,
    EpisodeOfCareReasonValueCodeableReference,
    EpisodeOfCareReasonValueReference,
    EpisodeOfCareReference,
    EpisodeOfCareStatusHistory,
)


class EpisodeOfCareReferenceSerializer(BaseReferenceModelSerializer):
    """Episode of care reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = EpisodeOfCareReference
        exclude = ["created_at", "updated_at"]


class EpisodeOfCareStatusHistorySerializer(WritableNestedModelSerializer):
    """Episode of care status history serializer."""

    period = PeriodSerializer(required=False)

    class Meta:
        """Meta class."""

        model = EpisodeOfCareStatusHistory
        exclude = ["created_at", "updated_at"]


class EpisodeOfCareReasonValueReferenceSerializer(BaseReferenceModelSerializer):
    """Episode of care reason value reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = EpisodeOfCareReasonValueReference
        exclude = ["created_at", "updated_at"]


class EpisodeOfCareReasonValueCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """Episode of care reason value codeable reference serializer."""

    reference = EpisodeOfCareReasonValueReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = EpisodeOfCareReasonValueCodeableReference
        exclude = ["created_at", "updated_at"]


class EpisodeOfCareReasonSerializer(WritableNestedModelSerializer):
    """Episode of care reason serializer."""

    use = CodeableConceptSerializer(many=False, required=False)
    value = EpisodeOfCareReasonValueCodeableReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = EpisodeOfCareReason
        exclude = ["created_at", "updated_at"]


class EpisodeOfCareDiagnosisSerializer(WritableNestedModelSerializer):
    """Episode of care diagnosis serializer."""

    condition = ConditionCodeableReferenceSerializer(many=False, required=False)
    use = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = EpisodeOfCareDiagnosis
        exclude = ["created_at", "updated_at"]


class EpisodeOfCareSerializer(BaseWritableNestedModelSerializer):
    """Episode of care serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    status_history = EpisodeOfCareStatusHistorySerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    diagnosis = EpisodeOfCareDiagnosisSerializer(many=True, required=False)
    subject = PatientGroupReferenceSerializer(many=False, required=False)
    managing_organization = OrganizationReferenceSerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)
    care_manager = PractitionerPractitionerRoleReferenceSerializer(
        many=False, required=False
    )
    care_team = CareTeamReferenceSerializer(many=True, required=False)
    referral_request = ServiceRequestReferenceSerializer(many=True, required=False)
    account = AccountReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = EpisodeOfCare
        exclude = ["created_at", "updated_at"]
