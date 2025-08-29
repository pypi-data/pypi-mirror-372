"""Nutrition Products serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AnnotationSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    QuantitySerializer,
    RatioSerializer,
)
from dfhir.substances.serializers import SubstanceCodeableReferenceSerializer

from .models import (
    NutritionProduct,
    NutritionProductCharacteristic,
    NutritionProductCodeableReference,
    NutritionProductIngredient,
    NutritionProductInstance,
    NutritionProductNutrients,
    NutritionProductReference,
)


class NutritionProductReferenceSerializer(BaseReferenceModelSerializer):
    """Nutrition Product Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionProductReference
        exclude = ["created_at", "updated_at"]


class NutritionProductCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Nutrition Product Codeable Reference serializer."""

    reference = NutritionProductReferenceSerializer(required=False)
    concept = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionProductCodeableReference
        exclude = ["created_at", "updated_at"]


class NutritionProductCharacteristicSerializer(WritableNestedModelSerializer):
    """Nutrition Product Characteristic serializer."""

    type = CodeableConceptSerializer(required=False)
    value_codeable_concept = CodeableConceptSerializer(required=False)
    value_quantity = QuantitySerializer(required=False)
    value_attachment = AttachmentSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionProductCharacteristic
        exclude = ["created_at", "updated_at"]


class NutritionProductInstanceSerializer(WritableNestedModelSerializer):
    """Nutrition Product Instance serializer."""

    quantity = QuantitySerializer(required=False)
    identifier = IdentifierSerializer(many=True, required=False)
    biological_source_event = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionProductInstance
        exclude = ["created_at", "updated_at"]


class NutritionProductNutrientsSerializer(WritableNestedModelSerializer):
    """Nutrition Product Nutrients serializer."""

    item = SubstanceCodeableReferenceSerializer(required=False)
    amount_ratio = RatioSerializer(required=False)
    amount_quantity = QuantitySerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionProductNutrients
        exclude = ["created_at", "updated_at"]


class NutritionProductIngredientSerializer(WritableNestedModelSerializer):
    """Nutrition Product Ingredient serializer."""

    item = NutritionProductCodeableReferenceSerializer(required=False)
    amount_ratio = RatioSerializer(required=False)
    amount_quantity = QuantitySerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionProductIngredient
        exclude = ["created_at", "updated_at"]


class NutritionProductSerializer(BaseWritableNestedModelSerializer):
    """Nutrition Product serializer."""

    code = CodeableConceptSerializer(required=False)
    status = serializers.CharField(required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    manufacturer = OrganizationReferenceSerializer(many=True, required=False)
    nutrient = NutritionProductNutrientsSerializer(many=True, required=False)
    ingredient = NutritionProductIngredientSerializer(many=True, required=False)
    energy = QuantitySerializer(required=False)
    characteristic = NutritionProductCharacteristicSerializer(many=True, required=False)
    instance = NutritionProductInstanceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = NutritionProduct
        exclude = ["created_at", "updated_at"]
