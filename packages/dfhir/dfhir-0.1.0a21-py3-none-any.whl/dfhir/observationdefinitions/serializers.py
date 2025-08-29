"""observation definitions serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodingSerializer,
    ContactDetailSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    RangeSerializer,
    UsageContextSerializer,
)
from dfhir.observationdefinitions.models import (
    ObservationDefinition,
    ObservationDefinitionComponent,
    ObservationDefinitionQualifiedValue,
    ObservationDefinitionQuestionnaireReference,
    ObservationDefinitionReference,
)
from dfhir.specimendefinitions.serializers import SpecimenDefinitionReferenceSerializer


class ObservationDefinitionQualifiedValueSerializer(WritableNestedModelSerializer):
    """Serializer for observation definition qualified values."""

    context = CodeableConceptSerializer(many=False, required=False)
    applies_to = CodeableConceptSerializer(many=False, required=False)
    age = RangeSerializer(many=False, required=False)
    gestational_age = RangeSerializer(many=False, required=False)
    range = RangeSerializer(many=False, required=False)
    interpretation = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = ObservationDefinitionQualifiedValue
        exclude = ["created_at", "updated_at"]


class ObservationDefinitionComponentSerializer(WritableNestedModelSerializer):
    """Serializer for observation definition components."""

    code = CodeableConceptSerializer(many=False, required=False)
    permitted_unit = CodingSerializer(many=True, required=False)
    qualified_value = ObservationDefinitionQualifiedValueSerializer(
        many=True, required=False
    )

    class Meta:
        """meta options."""

        model = ObservationDefinitionComponent
        exclude = ["created_at", "updated_at"]


class ObservationDefinitionQuestionnaireReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Serializer for observation definition questionnaire references."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ObservationDefinitionQuestionnaireReference
        exclude = ["created_at", "updated_at"]


class ObservationDefinitionSerializer(BaseWritableNestedModelSerializer):
    """Serializer for observation definitions."""

    identifier = IdentifierSerializer(many=False, required=False)
    version_algorithm_coding = CodingSerializer(many=False, required=False)
    contact = ContactDetailSerializer(many=True, required=False)
    use_context = UsageContextSerializer(many=True, required=False)
    jurisdiction = CodingSerializer(many=True, required=False)
    effective_period = PeriodSerializer(many=False, required=False)
    subject = CodingSerializer(many=True, required=False)
    performer_type = CodeableConceptSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    body_site = CodeableConceptSerializer(many=True, required=False)
    method = CodeableConceptSerializer(many=False, required=False)
    specimen = SpecimenDefinitionReferenceSerializer(required=False)
    permitted_unit = CodingSerializer(many=True, required=False)
    qualified_value = ObservationDefinitionQualifiedValueSerializer(
        many=True, required=False
    )
    has_member = ObservationDefinitionQuestionnaireReferenceSerializer(
        many=True, required=False
    )
    component = ObservationDefinitionComponentSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = ObservationDefinition
        exclude = ["created_at", "updated_at"]


class ObservationDefinitionReferenceSerializer(BaseReferenceModelSerializer):
    """Serializer for observation definition references."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ObservationDefinitionReference
        exclude = ["created_at", "updated_at"]
