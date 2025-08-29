"""CareTeam serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    ContactPointSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    TimingSerializer,
)
from dfhir.conditions.serializers import ConditionCodeableReferenceSerializer
from dfhir.patients.serializers import PatientGroupReferenceSerializer

from .models import (
    CareTeam,
    CareTeamParticipant,
    CareTeamParticipantMemberReference,
    CareTeamParticipantOnBehalfOfReference,
    CareTeamReference,
)


class CareTeamParticipantMemberReferenceSerializer(BaseReferenceModelSerializer):
    """Care Team Participant Member Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = CareTeamParticipantMemberReference
        exclude = ["created_at", "updated_at"]


class CareTeamParticipantOnBehalfOfReferenceSerializer(BaseReferenceModelSerializer):
    """Care Team Participant On Behalf Of Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = CareTeamParticipantOnBehalfOfReference
        exclude = ["created_at", "updated_at"]


class CareTeamParticipantSerializer(WritableNestedModelSerializer):
    """Care Team Participant serializer."""

    role = CodeableConceptSerializer(required=False)
    member = CareTeamParticipantMemberReferenceSerializer(required=False)
    on_behalf_of = CareTeamParticipantOnBehalfOfReferenceSerializer(required=False)
    effective_period = PeriodSerializer(required=False)
    effective_timing = TimingSerializer(required=False)

    class Meta:
        """Meta class."""

        model = CareTeamParticipant
        exclude = ["created_at", "updated_at"]


class CareTeamSerializer(BaseWritableNestedModelSerializer):
    """Care Team serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    subject = PatientGroupReferenceSerializer(required=False)
    period = PeriodSerializer(required=False)
    participant = CareTeamParticipantSerializer(many=True, required=False)
    reason = ConditionCodeableReferenceSerializer(many=True, required=False)
    managing_organization = OrganizationReferenceSerializer(many=True, required=False)
    telecom = ContactPointSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = CareTeam
        exclude = ["created_at", "updated_at"]


class CareTeamReferenceSerializer(BaseReferenceModelSerializer):
    """Care Team Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = CareTeamReference
        exclude = ["created_at", "updated_at"]
