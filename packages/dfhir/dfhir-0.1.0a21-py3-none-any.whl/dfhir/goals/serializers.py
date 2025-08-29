"""Goals serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    DurationSerializer,
    IdentifierSerializer,
    QuantitySerializer,
    RangeSerializer,
    RatioSerializer,
)

from .models import (
    Goal,
    GoalAcceptance,
    GoalAcceptanceParticipantReference,
    GoalAddressesReference,
    GoalSourceReference,
    GoalSubjectReference,
    GoalTarget,
)


class GoalSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """Goal Subject Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = GoalSubjectReference
        exclude = ["created_at", "updated_at"]


class GoalAcceptanceParticipantReferenceSerializer(BaseReferenceModelSerializer):
    """Goal Acceptance Participant Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = GoalAcceptanceParticipantReference
        exclude = ["created_at", "updated_at"]


class GoalAcceptanceSerializer(WritableNestedModelSerializer):
    """Goal Acceptance serializer."""

    participant = GoalAcceptanceParticipantReferenceSerializer(required=False)
    priority = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = GoalAcceptance
        exclude = ["created_at", "updated_at"]


class GoalTargetSerializer(WritableNestedModelSerializer):
    """Goal Target serializer."""

    measure = CodeableConceptSerializer(required=False)
    detail_quantity = QuantitySerializer(required=False)
    detail_range = RangeSerializer(required=False)
    detail_codeable_concept = CodeableConceptSerializer(required=False)
    detail_ratio = RatioSerializer(required=False)
    due_duration = DurationSerializer(required=False)

    class Meta:
        """Meta class."""

        model = GoalTarget
        exclude = ["created_at", "updated_at"]


class GoalSourceReferenceSerializer(BaseReferenceModelSerializer):
    """Goal Source Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = GoalSourceReference
        exclude = ["created_at", "updated_at"]


class GoalAddressesReferenceSerializer(BaseReferenceModelSerializer):
    """Goal Addresses Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = GoalAddressesReference
        exclude = ["created_at", "updated_at"]


class GoalSerializer(BaseWritableNestedModelSerializer):
    """Goal serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    achievement_status = CodeableConceptSerializer(required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    priority = CodeableConceptSerializer(required=False)
    description = CodeableConceptSerializer(required=False)
    subject = GoalSubjectReferenceSerializer(required=False)
    start_codeable_concept = CodeableConceptSerializer(required=False)
    acceptance = GoalAcceptanceSerializer(required=False, many=True)
    target = GoalTargetSerializer(many=True, required=False)
    status_reason = CodeableConceptSerializer(required=False, many=True)
    source = GoalSourceReferenceSerializer(required=False)
    addresses = GoalAddressesReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Goal
        exclude = ["created_at", "updated_at"]
