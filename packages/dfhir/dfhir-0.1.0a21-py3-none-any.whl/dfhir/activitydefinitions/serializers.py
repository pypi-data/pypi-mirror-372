"""activity definitions serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.activitydefinitions.models import (
    ActivityDefinition,
    ActivityDefinitionDynamicValue,
    ActivityDefinitionParticipant,
    ActivityDefinitionParticipantTypeReference,
    ActivityDefinitionPlanDefinitionCodeableReference,
    ActivityDefinitionPlanDefinitionReference,
    ActivityDefinitionProductProductReference,
    ActivityDefinitionReference,
    ActivityDefinitionSubjectReference,
)
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
    RelatedArtifactSerializer,
    TimingSerializer,
    UsageContextSerializer,
)
from dfhir.locations.serializers import LocationReferenceSerializer


class ActivityDefinitionPlanDefinitionReferenceSerializer(BaseReferenceModelSerializer):
    """activity plan definition reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ActivityDefinitionPlanDefinitionReference
        exclude = ["created_at", "updated_at"]


class ActivityDefinitionProductProductReferenceSerializer(BaseReferenceModelSerializer):
    """activity definition product reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ActivityDefinitionProductProductReference
        exclude = ["created_at", "updated_at"]


class ActivityDefinitionSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """activity definition subject reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ActivityDefinitionSubjectReference
        exclude = ["created_at", "updated_at"]


class ActivityDefinitionReferenceSerializer(BaseReferenceModelSerializer):
    """activity definition reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ActivityDefinitionReference
        exclude = ["created_at", "updated_at"]


class ActivityDefinitionParticipantTypeReferenceSerializer(
    BaseReferenceModelSerializer
):
    """activity definition participant type reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ActivityDefinitionParticipantTypeReference
        exclude = ["created_at", "updated_at"]


class ActivityDefinitionParticipantSerializer(WritableNestedModelSerializer):
    """activity definition participant serializer."""

    # type_canonical = CapabilityStatementCanonicalSerializer(many=False, required=False)
    type_reference = ActivityDefinitionParticipantTypeReferenceSerializer(
        many=False, required=False
    )
    role = CodeableConceptSerializer(required=False)
    function = CodeableConceptSerializer(required=False)

    class Meta:
        """meta options."""

        model = ActivityDefinitionParticipant
        exclude = ["created_at", "updated_at"]


class ActivityDefinitionDynamicValueSerializer(WritableNestedModelSerializer):
    """activity definition dynamic value serializer."""

    expression = ExpressionSerializer(required=False)

    class Meta:
        """meta options."""

        model = ActivityDefinitionDynamicValue
        exclude = ["created_at", "updated_at"]


class ActivityDefinitionSerializer(BaseWritableNestedModelSerializer):
    """activity definition serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    version_algorithm_coding = CodingSerializer(required=False)
    subject_codeable_concept = CodeableConceptSerializer(required=False)
    subject_reference = ActivityDefinitionSubjectReferenceSerializer(
        many=False, required=False
    )
    # subject_canonical = EvidenceVariableSerializer(required=False)
    contact = ContactDetailSerializer(required=False, many=True)
    use_context = UsageContextSerializer(many=True, required=False)
    jurisdiction = CodeableConceptSerializer(many=True, required=False)
    effective_period = PeriodSerializer(required=False)
    topic = CodeableConceptSerializer(many=True, required=False)
    author = ContactDetailSerializer(many=True, required=False)
    editor = ContactDetailSerializer(many=True, required=False)
    reviewer = ContactDetailSerializer(many=True, required=False)
    endorser = ContactDetailSerializer(many=True, required=False)
    kind = CodingSerializer(required=False)
    related_artifact = RelatedArtifactSerializer(many=True, required=False)
    # profile = StructuredDefinitionCanonical(required=False)
    # library = LibraryCanonicalReference(required=False)
    code = CodeableConceptSerializer(required=False)
    timing_timing = TimingSerializer(required=False)
    timing_age = AgeSerializer(required=False)
    timing_range = RangeSerializer(required=False)
    timing_duration = DurationSerializer(required=False)
    as_needed_codeable_concept = CodeableConceptSerializer(required=False)
    location = LocationReferenceSerializer(required=False)
    participant = ActivityDefinitionParticipantSerializer(many=True, required=False)
    product_reference = ActivityDefinitionProductProductReferenceSerializer(
        required=False
    )
    product_codeable_concept = CodeableConceptSerializer(required=False)
    quantity = QuantitySerializer(required=False)
    # dosage = DosageSerializer(required=False, many=True)
    body_site = CodeableConceptSerializer(many=True, required=False)
    # subject_requirements = SpecimenDefinitionCanonnicalSerializer(required=False)
    # observation_requirement = ObservationDefinitionCanonicalSerializer(required=False)
    # observation_result_requirement = ObservationDefinitionCanonicalSerializer(required=False)
    # transform = StructuredDefinitionCanonicalSerializer(required=False)
    dynamic_value = ActivityDefinitionDynamicValueSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = ActivityDefinition
        exclude = ["created_at", "updated_at"]


class ActivityDefinitionPlanDefinitionCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """activity plan definition codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = ActivityDefinitionPlanDefinitionReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = ActivityDefinitionPlanDefinitionCodeableReference
        exclude = ["created_at", "updated_at"]
