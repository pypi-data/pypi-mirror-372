"""Substance serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    RatioSerializer,
)

from .models import (
    Substance,
    SubstanceCodeableReference,
    SubstanceIngredient,
    SubstanceReference,
)


class SubstanceReferenceSerializer(BaseReferenceModelSerializer):
    """Substance Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = SubstanceReference
        exclude = ["created_at", "updated_at"]


class SubstanceCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Substance Codeable Reference serializer."""

    reference = SubstanceReferenceSerializer(required=False)
    concept = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = SubstanceCodeableReference
        exclude = ["created_at", "updated_at"]


class SubstanceIngredientSerializer(WritableNestedModelSerializer):
    """Substance Ingredient serializer."""

    quantity = RatioSerializer(required=False)
    substance_codeable_concept = CodeableConceptSerializer(required=False)
    substance_reference = SubstanceReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = SubstanceIngredient
        exclude = ["created_at", "updated_at"]


class SubstanceSerializer(BaseWritableNestedModelSerializer):
    """Substance serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    ingredient = SubstanceIngredientSerializer(required=False, many=True)

    class Meta:
        """Meta class."""

        model = Substance
        exclude = ["created_at", "updated_at"]
