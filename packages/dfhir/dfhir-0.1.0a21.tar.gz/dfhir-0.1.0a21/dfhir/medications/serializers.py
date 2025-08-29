"""medications serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    QuantitySerializer,
    RatioSerializer,
)
from dfhir.medications.models import (
    Medication,
    MedicationBatch,
    MedicationCodeableReference,
    MedicationCodes,
    MedicationDoseForm,
    MedicationIngredient,
    MedicationIngredientItem,
    MedicationReference,
    MedicationSubstanceCodeableReference,
    MedicationSubstanceReference,
)


class MedicationBatchSerializer(WritableNestedModelSerializer):
    """medication batch serializer."""

    class Meta:
        """metadata."""

        model = MedicationBatch
        exclude = ["created_at", "updated_at"]


class MedicationSubstanceReferenceSerializer(BaseReferenceModelSerializer):
    """medication substance reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """metadata."""

        model = MedicationSubstanceReference
        exclude = ["created_at", "updated_at"]


class MedicatonSubstanceCodeableReferenceSerializer(WritableNestedModelSerializer):
    """medication substance codeable reference serializer."""

    reference = MedicationSubstanceReferenceSerializer(required=False, many=False)
    concept = CodeableConceptSerializer(required=False, many=False)

    class Meta:
        """metadata."""

        model = MedicationSubstanceCodeableReference
        exclude = ["created_at", "updated_at"]


class MedicationIngredientSerializer(WritableNestedModelSerializer):
    """medication ingredient serializer."""

    item = MedicatonSubstanceCodeableReferenceSerializer(required=False, many=False)
    strength_quantity = QuantitySerializer(required=False, many=False)
    strength_ratio = RatioSerializer(required=False, many=False)
    strength_codeable_concept = CodeableConceptSerializer(required=False, many=False)

    class Meta:
        """metadata."""

        model = MedicationIngredient
        exclude = ["created_at", "updated_at"]


class MedicationSerializer(BaseWritableNestedModelSerializer):
    """medication serializer."""

    def get_fields(self):
        """Get fields."""
        from dfhir.medicationknowledges.serializers import (
            MedicationKnowledgeReferenceSerializer,
        )

        fields = super().get_fields()

        fields["definition"] = MedicationKnowledgeReferenceSerializer(
            required=False, many=False
        )

        return fields

    code = CodeableConceptSerializer(required=False, many=False)
    dose_form = CodeableConceptSerializer(required=False, many=False)
    batch = MedicationBatchSerializer(required=False, many=False)
    ingredient = MedicationIngredientSerializer(required=False, many=True)
    manufacturer = OrganizationReferenceSerializer(required=False, many=False)
    marketing_authorization_holder = OrganizationReferenceSerializer(
        required=False, many=False
    )

    class Meta:
        """metadata."""

        model = Medication
        exclude = ["created_at", "updated_at"]


class MedicationCodesSerializer(serializers.ModelSerializer):
    """medication codes serializer."""

    class Meta:
        """metadata."""

        model = MedicationCodes
        exclude = ["created_at", "updated_at"]


class MedicationDoseFormSerializer(serializers.ModelSerializer):
    """medication dose form serializer."""

    class Meta:
        """metadata."""

        model = MedicationDoseForm
        exclude = ["created_at", "updated_at"]


class MedicationIngredientItemSerializer(serializers.ModelSerializer):
    """medication ingredient item serializer."""

    class Meta:
        """metadata."""

        model = MedicationIngredientItem
        exclude = ["created_at", "updated_at"]


class MedicationReferenceSerializer(BaseReferenceModelSerializer):
    """medication reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """metadata."""

        model = MedicationReference
        exclude = ["created_at", "updated_at"]


class MedicationCodeableReferenceSerializer(WritableNestedModelSerializer):
    """medication codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False, many=False)
    reference = MedicationReferenceSerializer(required=False, many=False)

    class Meta:
        """metadata."""

        model = MedicationCodeableReference
        exclude = ["created_at", "updated_at"]
