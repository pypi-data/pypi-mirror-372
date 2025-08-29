"""nutrition intake serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    QuantitySerializer,
    RatioSerializer,
    ReferenceSerializer,
    TimingSerializer,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.nutritionintakes.models import (
    NutritionIntake,
    NutritionIntakeBasedOnReference,
    NutritionIntakeCodeableReference,
    NutritionIntakeNutritionItem,
    NutritionIntakeNutritionItemConsumedItem,
    NutritionIntakeNutritionItemTotalIntake,
    NutritionIntakePartOfReference,
    NutritionIntakePerformer,
    NutritionIntakePerformerActorReference,
    NutritionIntakeReasonCodeableReference,
    NutritionIntakeReasonReference,
    NutritionIntakeReference,
    NutritionIntakeReportedReference,
)
from dfhir.nutritionproducts.serializers import (
    NutritionProductCodeableReferenceSerializer,
)
from dfhir.patients.serializers import PatientGroupReferenceSerializer


class NutritionIntakeBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """nutrition intake based on reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionIntakeBasedOnReference
        exclude = ["created_at", "updated_at"]


class NutritionIntakePartOfReferenceSerializer(BaseReferenceModelSerializer):
    """nutrition intake part of reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionIntakePartOfReference
        exclude = ["created_at", "updated_at"]


class NutritionIntakePerformerActorReferenceSerializer(BaseReferenceModelSerializer):
    """nutrition intake performer actor reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = NutritionIntakePerformerActorReference
        exclude = ["created_at", "updated_at"]


class NutritionIntakeReportedReferenceSerializer(BaseReferenceModelSerializer):
    """nutrition intake reported reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionIntakeReportedReference
        exclude = ["created_at", "updated_at"]


class NutritionIntakeNutritionItemConsumedItemSerializer(WritableNestedModelSerializer):
    """nutrition intake nutrition item consumed item serializer."""

    schedule = TimingSerializer(required=False)
    amount = QuantitySerializer(required=False)
    rate_quantity = QuantitySerializer(required=False)
    rate_ratio = RatioSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionIntakeNutritionItemConsumedItem
        exclude = ["created_at", "updated_at"]


class NutritionIntakeNutritionItemTotalIntakeSerializer(WritableNestedModelSerializer):
    """nutrition intake nutrition item total intake serializer."""

    nutrient = CodeableConceptSerializer(required=False)
    amount = QuantitySerializer(required=False)
    energy = QuantitySerializer(required=False)

    class Meta:
        """meta option."""

        model = NutritionIntakeNutritionItemTotalIntake
        exclude = ["created_at", "updated_at"]


class NutritionIntakeNutritionItemSerializer(WritableNestedModelSerializer):
    """nutrition intake nutrition item serializer."""

    type = CodeableConceptSerializer(required=False)
    nutrition_product = NutritionProductCodeableReferenceSerializer(required=False)
    consumed_item = NutritionIntakeNutritionItemConsumedItemSerializer(
        required=False, many=True
    )
    total_intake = NutritionIntakeNutritionItemTotalIntakeSerializer(
        required=False, many=True
    )
    not_consumed_reason = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionIntakeNutritionItem
        exclude = ["created_at", "updated_at"]


class NutritionIntakePerformerSerializer(BaseReferenceModelSerializer):
    """nutrition intake performer reference serializer."""

    actor = NutritionIntakePerformerActorReferenceSerializer(required=False)
    function = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionIntakePerformer
        exclude = ["created_at", "updated_at"]


class NutritionIntakeReasonReferenceSerializer(BaseReferenceModelSerializer):
    """nutrition intake reason codeable reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionIntakeReasonReference
        exclude = ["created_at", "updated_at"]


class NutritionIntakeReasonCodeableReferenceSerializer(WritableNestedModelSerializer):
    """nutrition intake reason codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = ReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionIntakeReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class NutritionIntakeSerializer(BaseWritableNestedModelSerializer):
    """nutrition intake serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    based_on = NutritionIntakeBasedOnReferenceSerializer(required=False, many=True)
    part_of = NutritionIntakePartOfReferenceSerializer(required=False, many=True)
    status_reason = CodeableConceptSerializer(required=False, many=True)
    code = CodeableConceptSerializer(required=False)
    subject = PatientGroupReferenceSerializer(required=False)
    encounter = EncounterReferenceSerializer(required=False)
    occurrence_period = PeriodSerializer(required=False)
    reported_reference = NutritionIntakeReportedReferenceSerializer(required=False)
    nutrition_item = NutritionIntakeNutritionItemSerializer(required=False, many=True)
    performer = NutritionIntakePerformerSerializer(required=False, many=True)
    location = LocationReferenceSerializer(required=False)
    derived_from = ReferenceSerializer(required=False, many=True)
    reason_code = NutritionIntakeReasonCodeableReferenceSerializer(
        required=False, many=True
    )
    note = AnnotationSerializer(required=False, many=True)

    class Meta:
        """Meta class."""

        model = NutritionIntake
        exclude = ["created_at", "updated_at"]


class NutritionIntakeRefernce(BaseReferenceModelSerializer):
    """nutrition intake reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionIntakeReference
        exclude = ["created_at", "updated_at"]


class NutritionIntakeCodeableReferenceSerializer(WritableNestedModelSerializer):
    """nutrition intake codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = ReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = NutritionIntakeCodeableReference
        exclude = ["created_at", "updated_at"]
