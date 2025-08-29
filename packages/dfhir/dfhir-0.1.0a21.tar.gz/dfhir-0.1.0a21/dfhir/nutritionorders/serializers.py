"""nutrition order serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.allergyintolerances.serializers import AllergyIntoleranceReferenceSerializer
from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    QuantitySerializer,
    RatioSerializer,
    ReferenceSerializer,
    TimingSerializer,
)
from dfhir.devicedefinitions.serializers import (
    DeviceDefinitionCodeableReferenceSerializer,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.nutritionorders.models import (
    NutritionOrder,
    NutritionOrderAdditive,
    NutritionOrderBasedOnReference,
    NutritionOrderCodeableReference,
    NutritionOrderEnteralFormula,
    NutritionOrderEnteralFormulaAdministration,
    NutritionOrderOralDiet,
    NutritionOrderOralDietNutrient,
    NutritionOrderOralDietTexture,
    NutritionOrderPerformerReference,
    NutritionOrderReference,
    NutritionOrderSchedule,
    NutritionOrderSupplement,
)
from dfhir.nutritionproducts.serializers import (
    NutritionProductCodeableReferenceSerializer,
)
from dfhir.patients.serializers import PatientGroupReferenceSerializer
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)


class NutritionOrderReferenceSerializer(BaseReferenceModelSerializer):
    """nutrition order reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderReference
        exclude = ["created_at", "updated_at"]


class NutritionOrderCodeableReferenceSerializer(WritableNestedModelSerializer):
    """nutrition order codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = NutritionOrderReferenceSerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderCodeableReference
        exclude = ["created_at", "updated_at"]


class NutritionOrderScheduleSerializer(WritableNestedModelSerializer):
    """nutrition order schedule serializer."""

    timing = TimingSerializer(required=False, many=True)
    as_needed_for = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderSchedule
        exclude = ["created_at", "updated_at"]


class NutritionOrderOralDietNutrientSerializer(WritableNestedModelSerializer):
    """nutrition order oral diet nutrient serializer."""

    modifier = CodeableConceptSerializer(required=False)
    amount = QuantitySerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderOralDietNutrient
        exclude = ["created_at", "updated_at"]


class NutritionOrderOralDietTextureSerializer(WritableNestedModelSerializer):
    """nutrition order oral diet texture serializer."""

    modifier = CodeableConceptSerializer(required=False)
    type = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderOralDietTexture
        exclude = ["created_at", "updated_at"]


class NutritionOrderOralDietSerializer(WritableNestedModelSerializer):
    """nutrition order oral diet serializer."""

    type = CodeableConceptSerializer(required=False, many=True)
    schedule = NutritionOrderScheduleSerializer(required=False)
    nutrient = NutritionOrderOralDietNutrientSerializer(required=False, many=True)
    texture = NutritionOrderOralDietTextureSerializer(required=False, many=True)
    caloric_density = QuantitySerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderOralDiet
        exclude = ["created_at", "updated_at"]


class NutritionOrderSupplementSerializer(WritableNestedModelSerializer):
    """nutrition order supplement serializer."""

    type = NutritionProductCodeableReferenceSerializer(required=False)
    schedule = NutritionOrderScheduleSerializer(required=False, many=True)
    quantity = QuantitySerializer(required=False)
    caloric_density = QuantitySerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderSupplement
        exclude = ["created_at", "updated_at"]


class NutritionOrderEnteralFormulaAdministrationSerializer(
    WritableNestedModelSerializer
):
    """nutrition order enteral formula administration serializer."""

    schedule = NutritionOrderScheduleSerializer(required=False)
    quantity = QuantitySerializer(required=False)
    rate_quantity = QuantitySerializer(required=False)
    rate_ratio = RatioSerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderEnteralFormulaAdministration
        exclude = ["created_at", "updated_at"]


class NutritionOrderEnteralFormulaSerializer(WritableNestedModelSerializer):
    """nutrition order enteral formula serializer."""

    type = NutritionProductCodeableReferenceSerializer(required=False)
    delivery_device = DeviceDefinitionCodeableReferenceSerializer(
        required=False, many=True
    )
    caloric_density = QuantitySerializer(required=False)
    route_of_administration = CodeableConceptSerializer(required=False, many=True)
    administration = NutritionOrderEnteralFormulaAdministrationSerializer(
        required=False, many=True
    )
    max_volume_administer = QuantitySerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderEnteralFormula
        exclude = ["created_at", "updated_at"]


class NutritionOrderAdditiveSerializer(WritableNestedModelSerializer):
    """nutrition order additive serializer."""

    modular_type = NutritionProductCodeableReferenceSerializer(required=False)
    quantity = QuantitySerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderAdditive
        exclude = ["created_at", "updated_at"]


class NutritionOrderBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """nutrition order based on reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderBasedOnReference
        exclude = ["created_at", "updated_at"]


class NutritionOrderPerformerReferenceSerializer(BaseReferenceModelSerializer):
    """nutrition order performer reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = NutritionOrderPerformerReference
        exclude = ["created_at", "updated_at"]


class NutritionOrderSerializer(BaseWritableNestedModelSerializer):
    """nutrition order serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    # TODO: instantiates_canonical = NutritionOrderBasedOnReferenceSerializer(required=False, many=True)
    based_on = NutritionOrderBasedOnReferenceSerializer(required=False, many=True)
    group_identifier = IdentifierSerializer(required=False)
    subject = PatientGroupReferenceSerializer(required=False)
    encounter = EncounterReferenceSerializer(required=False)
    supporting_information = ReferenceSerializer(required=False, many=True)
    orderer = PractitionerPractitionerRoleReferenceSerializer(required=False)
    performer = NutritionOrderPerformerReferenceSerializer(required=False, many=True)
    allergy_intolerance = AllergyIntoleranceReferenceSerializer(
        required=False, many=True
    )
    food_preference_modifier = CodeableConceptSerializer(required=False, many=True)
    exclude_food_modifier = CodeableConceptSerializer(required=False, many=True)
    oral_diet = NutritionOrderOralDietSerializer(required=False)
    supplement = NutritionOrderSupplementSerializer(required=False, many=True)
    enteral_formula = NutritionOrderEnteralFormulaSerializer(required=False)
    additive = NutritionOrderAdditiveSerializer(required=False, many=True)
    note = AnnotationSerializer(required=False, many=True)

    class Meta:
        """Meta."""

        model = NutritionOrder
        exclude = ["created_at", "updated_at"]
