"""Plandefinitions serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AgeSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodingSerializer,
    ContactDetailSerializer,
    DurationSerializer,
    ExpressionSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    QuantitySerializer,
    RangeSerializer,
    RatioSerializer,
    RelatedArtifactSerializer,
    TimingSerializer,
    TriggerDefinitionSerializer,
    UsageContextSerializer,
)
from dfhir.groups.serializers import GroupReferenceSerializer
from dfhir.locations.serializers import LocationCodeableReferenceSerializer

from .models import (
    PlanDefinition,
    PlanDefinitionAction,
    PlanDefinitionActionCondition,
    PlanDefinitionActionDynamicValue,
    PlanDefinitionActionInput,
    PlanDefinitionActionOutput,
    PlanDefinitionActionParticipant,
    PlanDefinitionActionRelatedAction,
    PlanDefinitionActor,
    PlanDefinitionActorOptionTypeReferenceReference,
    PlanDefinitionGoal,
    PlanDefinitionGoalTarget,
    PlanDefinitionSubjectReference,
    PlanDefintionActorOption,
)


class PlanDefinitionSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """PlanDefinitionSubjectReferenceSerializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PlanDefinitionSubjectReference
        exclude = ["created_at", "updated_at"]


class PlanDefinitionActorOptionTypeReferenceReferenceSerializer(
    BaseReferenceModelSerializer
):
    """PlanDefinitionActorOptionTypeReferenceReferenceSerializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PlanDefinitionActorOptionTypeReferenceReference
        exclude = ["created_at", "updated_at"]


class PlanDefinitionActorOptionSerializer(WritableNestedModelSerializer):
    """PlanDefinitionActorOptionSerializer."""

    type_reference = PlanDefinitionActorOptionTypeReferenceReferenceSerializer(
        many=False, required=False
    )
    role = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PlanDefintionActorOption
        exclude = ["created_at", "updated_at"]


class PlanDefinitionActionConditionSerializer(WritableNestedModelSerializer):
    """PlanDefinitionActionConditionSerializer."""

    expression = ExpressionSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PlanDefinitionActionCondition
        exclude = ["created_at", "updated_at"]


class PlanDefinitionActionInputSerializer(WritableNestedModelSerializer):
    """PlanDefinitionActionInputSerializer."""

    class Meta:
        """Meta class."""

        model = PlanDefinitionActionInput
        exclude = ["created_at", "updated_at"]


class PlanDefinitionActionOutputSerializer(WritableNestedModelSerializer):
    """PlanDefinitionActionOutputSerializer."""

    class Meta:
        """Meta class."""

        model = PlanDefinitionActionOutput
        exclude = ["created_at", "updated_at"]


class PlanDefinitionActionParticipantSerializer(WritableNestedModelSerializer):
    """PlanDefinitionActionParticipantSerializer."""

    type_reference = PlanDefinitionActorOptionTypeReferenceReferenceSerializer(
        many=False, required=False
    )
    role = CodeableConceptSerializer(many=False, required=False)
    function = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PlanDefinitionActionParticipant
        exclude = ["created_at", "updated_at"]


class PlanDefinitionActionDynamicValueSerializer(WritableNestedModelSerializer):
    """PlanDefinitionActionDynamicValueSerializer."""

    expression = ExpressionSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PlanDefinitionActionDynamicValue
        exclude = ["created_at", "updated_at"]


class PlanDefinitionActionRelatedActionSerializer(WritableNestedModelSerializer):
    """PlanDefinitionActionRelatedActionSerializer."""

    offset_duration = DurationSerializer(many=False, required=False)
    offset_range = RangeSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PlanDefinitionActionRelatedAction
        exclude = ["created_at", "updated_at"]


class PlanDefinitionActionSerializer(WritableNestedModelSerializer):
    """PlanDefinitionActionSerializer."""

    code = CodeableConceptSerializer(many=False, required=False)
    reason = CodeableConceptSerializer(many=True, required=False)
    documentation = RelatedArtifactSerializer(many=True, required=False)
    subject_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    subject_reference = GroupReferenceSerializer(many=False, required=False)
    trigger = TriggerDefinitionSerializer(many=True, required=False)
    condition = PlanDefinitionActionConditionSerializer(many=True, required=False)
    input = PlanDefinitionActionInputSerializer(many=True, required=False)
    output = PlanDefinitionActionOutputSerializer(many=True, required=False)
    related_action = PlanDefinitionActionRelatedActionSerializer(
        many=True, required=False
    )
    timing_age = AgeSerializer(many=False, required=False)
    timing_duration = DurationSerializer(many=False, required=False)
    timing_range = RangeSerializer(many=False, required=False)
    timing_timing = TimingSerializer(many=False, required=False)
    location = LocationCodeableReferenceSerializer(many=False, required=False)
    participant = PlanDefinitionActionParticipantSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    dynamic_value = PlanDefinitionActionDynamicValueSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = PlanDefinitionAction
        exclude = ["created_at", "updated_at"]


class PlanDefinitionActorSerializer(WritableNestedModelSerializer):
    """PlanDefinitionActorSerializer."""

    option = PlanDefinitionActorOptionSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = PlanDefinitionActor
        exclude = ["created_at", "updated_at"]


class PlanDefinitionGoalTargetSerializer(WritableNestedModelSerializer):
    """PlanDefinitionGoalTargetSerializer."""

    measure = CodeableConceptSerializer(many=False, required=False)
    detail_quantity = QuantitySerializer(many=False, required=False)
    detail_range = RangeSerializer(many=False, required=False)
    detail_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    detail_ratio = RatioSerializer(many=False, required=False)
    due = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PlanDefinitionGoalTarget
        exclude = ["created_at", "updated_at"]


class PlanDefinitionGoalSerializer(WritableNestedModelSerializer):
    """PlanDefinitionGoalSerializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    description = CodeableConceptSerializer(many=False, required=False)
    priority = CodeableConceptSerializer(many=False, required=False)
    start = CodeableConceptSerializer(many=False, required=False)
    addresses = CodeableConceptSerializer(many=True, required=False)
    documentation = RelatedArtifactSerializer(many=True, required=False)
    target = PlanDefinitionGoalTargetSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = PlanDefinitionGoal
        exclude = ["created_at", "updated_at"]


class PlanDefinitionSerializer(BaseWritableNestedModelSerializer):
    """PlanDefinitionSerializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    version_algorithm_coding = CodingSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    subject_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    subject_reference = PlanDefinitionSubjectReferenceSerializer(
        many=False, required=False
    )
    contact = ContactDetailSerializer(many=True, required=False)
    use_context = UsageContextSerializer(many=True, required=False)
    jurisdiction = CodeableConceptSerializer(many=True, required=False)
    effective_period = PeriodSerializer(many=False, required=False)
    topic = CodeableConceptSerializer(many=True, required=False)
    author = ContactDetailSerializer(many=True, required=False)
    editor = ContactDetailSerializer(many=True, required=False)
    reviewer = ContactDetailSerializer(many=True, required=False)
    endorser = ContactDetailSerializer(many=True, required=False)
    related_artifact = RelatedArtifactSerializer(many=True, required=False)
    goal = PlanDefinitionGoalSerializer(many=True, required=False)
    actor = PlanDefinitionActorSerializer(many=True, required=False)
    action = PlanDefinitionActionSerializer(many=True, required=False)
    as_needed_codeable_concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PlanDefinition
        exclude = ["created_at", "updated_at"]
