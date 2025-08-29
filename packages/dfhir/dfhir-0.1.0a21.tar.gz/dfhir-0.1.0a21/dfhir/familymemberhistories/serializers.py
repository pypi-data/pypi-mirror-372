"""Family member history serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AgeSerializer,
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    RangeSerializer,
)
from dfhir.patients.serializers import PatientReferenceSerializer

from .models import (
    FamilyMemberHistory,
    FamilyMemberHistoryCondition,
    FamilyMemberHistoryParticipant,
    FamilyMemberHistoryParticipantActorReference,
    FamilyMemberHistoryProcedure,
    FamilyMemberHistoryReasonCodeableReference,
    FamilyMemberHistoryReasonReference,
)


class FamilyMemberHistoryReasonReferenceSerializer(BaseReferenceModelSerializer):
    """Family Member History Reason Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = FamilyMemberHistoryReasonReference
        exclude = ["created_at", "updated_at"]


class FamilyMemberHistoryReasonCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """Family Member History Reason Codeable Reference serializer."""

    concept = CodeableConceptSerializer(many=False, required=False)
    reference = FamilyMemberHistoryReasonReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = FamilyMemberHistoryReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class FamilyMemberHistoryConditionSerializer(WritableNestedModelSerializer):
    """Family Member History Condition serializer."""

    code = CodeableConceptSerializer(many=False, required=False)
    outcome = CodeableConceptSerializer(many=False, required=False)
    onset_age = AgeSerializer(many=False, required=False)
    onset_range = RangeSerializer(many=False, required=False)
    onset_period = PeriodSerializer(many=False, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = FamilyMemberHistoryCondition
        exclude = ["created_at", "updated_at"]


class FamilyMemberHistoryParticipantActorReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Family Member History Participant Actor Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = FamilyMemberHistoryParticipantActorReference
        exclude = ["created_at", "updated_at"]


class FamilyMemberHistoryParticipantSerializer(WritableNestedModelSerializer):
    """Family Member History Participant serializer."""

    function = CodeableConceptSerializer(many=False, required=False)
    actor = FamilyMemberHistoryParticipantActorReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta options."""

        model = FamilyMemberHistoryParticipant
        exclude = ["created_at", "updated_at"]


class FamilyMemberHistoryProcedureSerializer(WritableNestedModelSerializer):
    """Family Member History Procedure serializer."""

    code = CodeableConceptSerializer(many=False, required=False)
    outcome = CodeableConceptSerializer(many=False, required=False)
    performed_age = AgeSerializer(many=False, required=False)
    performed_range = RangeSerializer(many=False, required=False)
    performed_period = PeriodSerializer(many=False, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = FamilyMemberHistoryProcedure
        exclude = ["created_at", "updated_at"]


class FamilyMemberHistorySerializer(BaseWritableNestedModelSerializer):
    """Family Member History serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    data_absent_reason = CodeableConceptSerializer(many=False, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)
    participant = FamilyMemberHistoryParticipantSerializer(many=True, required=False)
    name = serializers.CharField(max_length=255, required=False)
    relationship = CodeableConceptSerializer(many=False, required=False)
    sex = CodeableConceptSerializer(many=False, required=False)
    born_period = PeriodSerializer(many=False, required=False)
    age_age = AgeSerializer(many=False, required=False)
    age_range = RangeSerializer(many=False, required=False)
    deceased_age = AgeSerializer(many=False, required=False)
    deceased_range = RangeSerializer(many=False, required=False)
    reason = FamilyMemberHistoryReasonCodeableReferenceSerializer(
        many=True, required=False
    )
    note = AnnotationSerializer(many=True, required=False)
    condition = FamilyMemberHistoryConditionSerializer(many=True, required=False)
    procedure = FamilyMemberHistoryProcedureSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = FamilyMemberHistory
        exclude = ["created_at", "updated_at"]
