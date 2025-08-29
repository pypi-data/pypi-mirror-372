"""Specimen definition serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodingSerializer,
    ContactDetailSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    QuantitySerializer,
    RangeSerializer,
    UsageContextSerializer,
)
from dfhir.groups.serializers import GroupReferenceSerializer

from .models import (
    SpecimenDefinition,
    SpecimenDefinitionReference,
    SpecimenDefinitionTypeTested,
    SpecimenDefinitionTypeTestedContainer,
    SpecimenDefinitionTypeTestedContainerAdditive,
    SpecimenDefinitionTypeTestedHandling,
)


class SpecimenDefinitionReferenceSerializer(BaseReferenceModelSerializer):
    """Serializer for specimen definition reference."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = SpecimenDefinitionReference
        exclude = ["created_at", "updated_at"]


class SpecimenDefinitionTypeTestedContainerAdditiveSerializer(
    WritableNestedModelSerializer
):
    """Serializer for specimen definition type tested container additive."""

    additive_codeable_concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = SpecimenDefinitionTypeTestedContainerAdditive
        exclude = ["created_at", "updated_at"]


class SpecimenDefinitionTypeTestedContainerSerializer(WritableNestedModelSerializer):
    """Serializer for specimen definition type tested container."""

    material = CodeableConceptSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    cap = CodeableConceptSerializer(many=False, required=False)
    capacity = QuantitySerializer(many=False, required=False)
    minimum_volume_quantity = QuantitySerializer(many=False, required=False)
    additive = SpecimenDefinitionTypeTestedContainerAdditiveSerializer(
        many=True, required=False
    )

    class Meta:
        """meta options."""

        model = SpecimenDefinitionTypeTestedContainer
        exclude = ["created_at", "updated_at"]


class SpecimenDefinitionTypeTestedHandlingSerializer(WritableNestedModelSerializer):
    """Serializer for specimen definition type tested handling."""

    temperature_qualifier = CodeableConceptSerializer(many=False, required=False)
    temperature_range = RangeSerializer(many=False, required=False)
    max_duration = QuantitySerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = SpecimenDefinitionTypeTestedHandling
        exclude = ["created_at", "updated_at"]


class SpecimenDefinitionTypeTestedSerializer(WritableNestedModelSerializer):
    """Serializer for specimen definition type tested."""

    type = CodeableConceptSerializer(many=False, required=False)
    container = SpecimenDefinitionTypeTestedContainerSerializer(
        many=False, required=False
    )
    retention_time = QuantitySerializer(many=False, required=False)
    retention_criterion = CodeableConceptSerializer(many=True, required=False)
    handling = SpecimenDefinitionTypeTestedHandlingSerializer(many=True, required=False)
    testing_destination = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = SpecimenDefinitionTypeTested
        exclude = ["created_at", "updated_at"]


class SpecimenDefinitionSerializer(BaseWritableNestedModelSerializer):
    """Serializer for specimen definition."""

    identifier = IdentifierSerializer(many=False, required=False)
    version_algorithm_coding = CodingSerializer(many=False, required=False)
    subject_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    subject_reference = GroupReferenceSerializer(many=False, required=False)
    contact = ContactDetailSerializer(many=True, required=False)
    use_context = UsageContextSerializer(many=True, required=False)
    jurisdiction = CodeableConceptSerializer(many=True, required=False)
    effective_period = PeriodSerializer(many=False, required=False)
    type_collected = CodeableConceptSerializer(many=False, required=False)
    patient_preparation = CodeableConceptSerializer(many=True, required=False)
    collection = CodeableConceptSerializer(many=True, required=False)
    type_tested = SpecimenDefinitionTypeTestedSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = SpecimenDefinition
        exclude = ["created_at", "updated_at"]
