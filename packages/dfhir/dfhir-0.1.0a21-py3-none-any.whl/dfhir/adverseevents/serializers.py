"""Adverse events serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
)
from dfhir.conditions.serializers import (
    ConditionObservationCodeableReferenceSerializer,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer

from .models import (
    AdverseEvent,
    AdverseEventContributingFactorCodeableReference,
    AdverseEventContributingFactorReference,
    AdverseEventMitigatingActionCodeableReference,
    AdverseEventMitigatingActionReference,
    AdverseEventParticipant,
    AdverseEventParticipantActorReference,
    AdverseEventPreventiveActionCodeableReference,
    AdverseEventPreventiveActionReference,
    AdverseEventRecorderReference,
    AdverseEventSubjectReference,
    AdverseEventSupportingInfoCodeableReference,
    AdverseEventSupportingInfoReference,
    AdverseEventSuspectEntity,
    AdverseEventSuspectEntityAuthorReference,
    AdverseEventSuspectEntityCausality,
    AdverseEventSuspectEntityInstanceCodeableReference,
    AdverseEventSuspectEntityInstanceReference,
)


class AdverseEventParticipantActorReferenceSerializer(BaseReferenceModelSerializer):
    """Adverse Event Participant Actor Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventParticipantActorReference
        exclude = ["created_at", "updated_at"]


class AdverseEventRecorderReferenceSerializer(BaseReferenceModelSerializer):
    """Adverse Event Recorder Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventRecorderReference
        exclude = ["created_at", "updated_at"]


class AdverseEventSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """Adverse Event Subject Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventSubjectReference
        exclude = ["created_at", "updated_at"]


class AdverseEventParticipantSerializer(BaseWritableNestedModelSerializer):
    """Adverse Event Participant Serializer."""

    actor = AdverseEventParticipantActorReferenceSerializer(many=False, required=False)
    function = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventParticipant
        exclude = ["created_at", "updated_at"]


class AdverseEventSuspectEntityInstanceReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Adverse Event Suspect Entity Instance Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventSuspectEntityInstanceReference
        exclude = ["created_at", "updated_at"]


class AdverseEventSuspectEntityInstanceCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """Adverse Event Suspect Entity Instance Codeable Reference Serializer."""

    reference = AdverseEventSuspectEntityInstanceReferenceSerializer(
        many=False, required=False
    )
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventSuspectEntityInstanceCodeableReference
        exclude = ["created_at", "updated_at"]


class AdverseEventSuspectEntityAuthorReferenceSerializer(BaseReferenceModelSerializer):
    """Adverse Event Suspect Entity Author Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventSuspectEntityAuthorReference
        exclude = ["created_at", "updated_at"]


class AdverseEventContributingFactorReferenceSerializer(BaseReferenceModelSerializer):
    """Adverse Event Contributing Factor Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventContributingFactorReference
        exclude = ["created_at", "updated_at"]


class AdverseEventContributingFactorCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """Adverse Event Contributing Factor Codeable Reference Serializer."""

    reference = AdverseEventContributingFactorReferenceSerializer(
        many=False, required=False
    )
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventContributingFactorCodeableReference
        exclude = ["created_at", "updated_at"]


class AdverseEventMitigatingActionReferenceSerializer(BaseReferenceModelSerializer):
    """Adverse Event Mitigating Action Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventMitigatingActionReference
        exclude = ["created_at", "updated_at"]


class AdverseEventMitigatingActionCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """Adverse Event Mitigating Action Codeable Reference Serializer."""

    reference = AdverseEventMitigatingActionReferenceSerializer(
        many=False, required=False
    )
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventMitigatingActionCodeableReference
        exclude = ["created_at", "updated_at"]


class AdverseEventPreventiveActionReferenceSerializer(BaseReferenceModelSerializer):
    """Adverse Event Preventive Action Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventPreventiveActionReference
        exclude = ["created_at", "updated_at"]


class AdverseEventPreventiveActionCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """Adverse Event Preventive Action Codeable Reference Serializer."""

    reference = AdverseEventPreventiveActionReferenceSerializer(
        many=False, required=False
    )
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventPreventiveActionCodeableReference
        exclude = ["created_at", "updated_at"]


class AdverseEventSupportingInfoReferenceSerializer(BaseReferenceModelSerializer):
    """Adverse Event Supporting Info Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventSupportingInfoReference
        exclude = ["created_at", "updated_at"]


class AdverseEventSupportingInfoCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """Adverse Event Supporting Info Codeable Reference Serializer."""

    reference = AdverseEventSupportingInfoReferenceSerializer(
        many=False, required=False
    )
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventSupportingInfoCodeableReference
        exclude = ["created_at", "updated_at"]


class AdverseEventSuspectEntityCausalitySerializer(BaseWritableNestedModelSerializer):
    """Adverse Event Suspect Entity Causality Serializer."""

    assessment_method = CodeableConceptSerializer(many=False, required=False)
    entity_relatedness = CodeableConceptSerializer(many=False, required=False)
    author = AdverseEventSuspectEntityAuthorReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = AdverseEventSuspectEntityCausality
        exclude = ["created_at", "updated_at"]


class AdverseEventSuspectEntitySerializer(BaseWritableNestedModelSerializer):
    """Adverse Event Suspect Entity Serializer."""

    instance = AdverseEventSuspectEntityInstanceCodeableReferenceSerializer(
        many=False, required=False
    )
    causality = AdverseEventSuspectEntityCausalitySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = AdverseEventSuspectEntity
        exclude = ["created_at", "updated_at"]


class AdverseEventSerializer(BaseWritableNestedModelSerializer):
    """Adverse Event Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    subject = AdverseEventSubjectReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    cause_period = PeriodSerializer(many=False, required=False)
    effect_period = PeriodSerializer(many=False, required=False)
    resulting_effect = ConditionObservationCodeableReferenceSerializer(
        many=True, required=False
    )
    location = LocationReferenceSerializer(many=False, required=False)
    seriousness = CodeableConceptSerializer(many=False, required=False)
    outcome = CodeableConceptSerializer(many=True, required=False)
    recorder = AdverseEventRecorderReferenceSerializer(many=False, required=False)
    participant = AdverseEventParticipantSerializer(many=True, required=False)
    suspect_entity = AdverseEventSuspectEntitySerializer(many=True, required=False)
    contributing_factor = AdverseEventContributingFactorCodeableReferenceSerializer(
        many=True, required=False
    )
    preventive_action = AdverseEventPreventiveActionCodeableReferenceSerializer(
        many=True, required=False
    )
    mitigating_action = AdverseEventMitigatingActionCodeableReferenceSerializer(
        many=True, required=False
    )
    supporting_info = AdverseEventSupportingInfoCodeableReferenceSerializer(
        many=True, required=False
    )
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = AdverseEvent
        exclude = ["created_at", "updated_at"]
