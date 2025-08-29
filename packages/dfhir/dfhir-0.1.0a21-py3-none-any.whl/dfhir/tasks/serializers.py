"""task serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    CodeableConceptSerializer,
    CodeableReferenceSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    ReferenceSerializer,
)
from dfhir.coverages.serializers import CoverageClaimResponseReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.provenances.serializers import ProvenanceReferenceSerializer
from dfhir.tasks.models import (
    Task,
    TaskInput,
    TaskOutput,
    TaskOwnerReference,
    TaskPerformer,
    TaskPerformerActorReference,
    TaskReference,
    TaskRequestedPerformerCodeableReference,
    TaskRequestedPerformerReference,
    TaskRequesterReference,
    TaskRestriction,
    TaskRestrictionRecipientReference,
)


class TaskReferenceSerializer(BaseReferenceModelSerializer):
    """Task reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskReference
        exclude = ["created_at", "updated_at"]


class TaskRequesterReferenceSerializer(BaseReferenceModelSerializer):
    """Task requester reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskRequesterReference
        exclude = ["created_at", "updated_at"]


class TaskRequestedPerformerReferenceSerializer(BaseReferenceModelSerializer):
    """Task requested performer reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskRequestedPerformerReference
        exclude = ["created_at", "updated_at"]


class TaskRequestedPerformerCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Task requested performer codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = TaskRequestedPerformerReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskRequestedPerformerCodeableReference
        exclude = ["created_at", "updated_at"]


class TaskOwnerReferenceSerializer(BaseReferenceModelSerializer):
    """Task owner reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskOwnerReference
        exclude = ["created_at", "updated_at"]


class TaskPerformerActorReferenceSerializer(BaseReferenceModelSerializer):
    """Task performer actor reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskPerformerActorReference
        exclude = ["created_at", "updated_at"]


class TaskRestrictionRecipientReferenceSerializer(BaseReferenceModelSerializer):
    """Task restriction recipient reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskRestrictionRecipientReference
        exclude = ["created_at", "updated_at"]


class TaskPerformerSerializer(WritableNestedModelSerializer):
    """Task performer serializer."""

    function = CodeableConceptSerializer(required=False)
    actor = TaskPerformerActorReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskPerformer
        exclude = ["created_at", "updated_at"]


class TaskRestrictionSerializer(WritableNestedModelSerializer):
    """Task restriction serializer."""

    period = PeriodSerializer(required=False)
    recipient = TaskRestrictionRecipientReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskRestriction
        exclude = ["created_at", "updated_at"]


class TaskInputSerializer(WritableNestedModelSerializer):
    """Task input serializer."""

    type = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskInput
        exclude = ["created_at", "updated_at"]


class TaskOutputSerializer(WritableNestedModelSerializer):
    """Task output serializer."""

    type = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = TaskOutput
        exclude = ["created_at", "updated_at"]


class TaskSerializer(WritableNestedModelSerializer):
    """Task serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    # instantiates_canonical = TaskReferenceSerializer(required=False,many=True)
    based_on = ReferenceSerializer(required=False, many=True)
    group_identifier = IdentifierSerializer(required=False)
    part_of = TaskReferenceSerializer(required=False, many=True)
    status_reason = CodeableConceptSerializer(required=False)
    business_status = CodeableConceptSerializer(required=False)
    code = CodeableConceptSerializer(required=False)
    focus = ReferenceSerializer(required=False, many=False)
    for_value = ReferenceSerializer(required=False, many=False)
    encounter = EncounterReferenceSerializer(required=False)
    requested_period = PeriodSerializer(required=False)
    execution_period = PeriodSerializer(required=False)
    requester = TaskRequesterReferenceSerializer(required=False)
    requested_performer = TaskRequestedPerformerCodeableReferenceSerializer(
        required=False, many=True
    )
    owner = TaskOwnerReferenceSerializer(required=False)
    performer = TaskPerformerSerializer(required=False, many=True)
    location = LocationReferenceSerializer(required=False)
    reason = CodeableReferenceSerializer(required=False, many=True)
    insurance = CoverageClaimResponseReferenceSerializer(required=False, many=True)
    note = AnnotationSerializer(required=False, many=True)
    relevant_history = ProvenanceReferenceSerializer(required=False, many=True)
    restriction = TaskRestrictionSerializer(required=False)
    input = TaskInputSerializer(required=False, many=True)
    output = TaskOutputSerializer(required=False, many=True)

    class Meta:
        """Meta class."""

        model = Task
        exclude = ["created_at", "updated_at"]
        rename_fields = {
            "for": "for_value",
        }
