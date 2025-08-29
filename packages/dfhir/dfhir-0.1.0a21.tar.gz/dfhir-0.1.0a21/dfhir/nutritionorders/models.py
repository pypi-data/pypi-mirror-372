"""nutrition orders models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    Reference,
    TimeStampedModel,
    Timing,
)
from dfhir.devicedefinitions.models import DeviceDefinitionCodeableReference
from dfhir.nutritionorders.choices import (
    NutritionOrderIntentChoices,
    NutritionOrderPriorityChoices,
    NutritionOrderStatusChoices,
)
from dfhir.patients.models import PatientGroupReference
from dfhir.practitioners.models import PractitionerPractitionerRoleReference


class NutritionOrderReference(BaseReference):
    """nutrition order reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_reference_identifier",
    )
    nutrition_order = models.ForeignKey(
        "NutritionOrder",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_reference_nutrition_order",
    )


class NutritionOrderCodeableReference(TimeStampedModel):
    """nutrition order codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        NutritionOrderReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_codeable_reference_reference",
    )


class NutritionOrderSchedule(TimeStampedModel):
    """nutrition order oral diet schedule model."""

    timing = models.ManyToManyField(
        Timing,
        related_name="nutrition_order_oral_diet_schedule_timing",
        blank=True,
    )
    as_needed = models.BooleanField(default=False)
    as_needed_for = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        related_name="nutrition_order_oral_diet_schedule_as_needed_for",
        null=True,
    )


class NutritionOrderOralDietNutrient(TimeStampedModel):
    """nutrition order oral diet nutrient model."""

    modifier = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        related_name="nutrition_order_oral_diet_nutrient_modifier",
        null=True,
    )
    amount = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        related_name="nutrition_order_oral_diet_nutrient_amount",
        null=True,
    )


class NutritionOrderOralDietTexture(TimeStampedModel):
    """nutrition order oral diet texture model."""

    modifier = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        related_name="nutrition_order_oral_diet_texture_modifier",
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        related_name="nutrition_order_oral_diet_texture_food_type",
        null=True,
    )


class NutritionOrderOralDiet(TimeStampedModel):
    """nutrition order oral diet model."""

    type = models.ManyToManyField(
        CodeableConcept, related_name="nutrition_order_oral_diet_type"
    )
    schedule = models.ForeignKey(
        NutritionOrderSchedule,
        related_name="nutrition_order_oral_diet_schedule",
        null=True,
        on_delete=models.DO_NOTHING,
    )
    nutrient = models.ManyToManyField(
        NutritionOrderOralDietNutrient,
        related_name="nutrition_order_oral_diet_nutrient",
        blank=True,
    )
    texture = models.ManyToManyField(
        NutritionOrderOralDietTexture,
        related_name="nutrition_order_oral_diet_texture",
        blank=True,
    )
    instruction = models.TextField(blank=True)
    caloric_density = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        related_name="nutrition_order_oral_diet_caloric_density",
        null=True,
    )


class NutritionOrderSupplement(TimeStampedModel):
    """nutrition order supplement model."""

    type = models.ForeignKey(
        "nutritionproducts.NutritionProductCodeableReference",
        on_delete=models.SET_NULL,
        related_name="nutrition_order_supplement_type",
        null=True,
    )
    productName = models.CharField(max_length=255, blank=True)
    schedule = models.ForeignKey(
        NutritionOrderSchedule,
        related_name="nutrition_order_supplement_schedule",
        null=True,
        on_delete=models.DO_NOTHING,
    )
    quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        related_name="nutrition_order_supplement_quantity",
        null=True,
    )
    instruction = models.TextField(blank=True)
    caloric_density = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_supplement_caloric_density",
    )


class NutritionOrderEnteralFormulaAdministration(TimeStampedModel):
    """nutrition order enteral formula administration model."""

    schedule = models.ForeignKey(
        NutritionOrderSchedule,
        on_delete=models.SET_NULL,
        related_name="nutrition_order_enternal_formula_administration_schedule",
        null=True,
    )
    quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        related_name="nutrition_order_enternal_formula_administration_quantity",
        null=True,
    )
    rate_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        related_name="nutrition_order_enternal_formula_administration_rate_quantity",
        null=True,
    )
    rate_ratio = models.ForeignKey(
        "base.Ratio",
        on_delete=models.SET_NULL,
        related_name="nutrition_order_enternal_formula_administration_rate_ratio",
        null=True,
    )


class NutritionOrderEnteralFormula(TimeStampedModel):
    """nutrition order enteral formula model."""

    type = models.ForeignKey(
        "nutritionproducts.NutritionProductCodeableReference",
        on_delete=models.SET_NULL,
        related_name="nutrition_order_enternal_formula_type",
        null=True,
    )
    product_name = models.CharField(max_length=255, null=True)
    delivery_Device = models.ManyToManyField(
        DeviceDefinitionCodeableReference,
        related_name="nutrition_order_enternal_formula_delivery_device",
        blank=True,
    )
    caloric_density = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        related_name="nutrition_order_enternal_formula_caloric_density",
        null=True,
    )
    route_of_administration = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="nutrition_order_enternal_formula_route_of_administration",
    )
    administration = models.ManyToManyField(
        NutritionOrderEnteralFormulaAdministration,
        related_name="nutrition_order_enternal_formula_administration",
        blank=True,
    )
    max_volume_to_administer = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_enternal_formula_max_volume_to_administer",
    )
    administration_instruction = models.TextField(null=True)


class NutritionOrderAdditive(TimeStampedModel):
    """nutrition order additive model."""

    modular_type = models.ForeignKey(
        "nutritionproducts.NutritionProductCodeableReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_additive_modular_type",
    )
    product_name = models.CharField(max_length=255, blank=True)
    quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_additive_quantity",
    )


class NutritionOrderBasedOnReference(BaseReference):
    """nutrition order based on reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_based_on_reference_identifier",
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_based_on_reference_care_plan",
    )
    nutrition_order = models.ForeignKey(
        "NutritionOrder",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_based_on_reference_nutrition_order",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_based_on_reference_service_request",
    )
    # TODO: request_orchestration = models.ForeignKey(
    #     "requestorchestrations.RequestOrchestration",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     related_name="nutrition_order_based_on_reference_request_orchestration",
    # )


class NutritionOrderPerformerReference(BaseReference):
    """nutrition order performer reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_performer_reference_identifier",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_performer_reference_care_team",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_performer_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_performer_reference_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_performer_reference_related_person",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_performer_reference_patient",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_performer_reference_organization",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.SET_NULL,
        null=True,
        related_name="nutrition_order_performer_reference_group",
    )


class NutritionOrder(TimeStampedModel):
    """Nutrition Order model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="nutrition_order_identifier"
    )
    # TODO: instantiates_canonical = models.ManyToManyField(ActivityDefintionPlanDefinitionCanonicalReference)
    instantiates_uri = models.URLField(null=True)
    instantiates = models.URLField(null=True)
    based_on = models.ManyToManyField(
        NutritionOrderBasedOnReference,
        blank=True,
        related_name="nutrition_order_based_on",
    )
    group_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_order_group_identifier",
    )
    status = models.CharField(
        max_length=255, blank=True, choices=NutritionOrderStatusChoices.choices
    )
    intent = models.CharField(
        max_length=255, null=True, choices=NutritionOrderIntentChoices.choices
    )
    priority = models.CharField(
        max_length=255, null=True, choices=NutritionOrderPriorityChoices.choices
    )
    subject = models.ForeignKey(
        PatientGroupReference,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_order_subject",
        null=True,
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        related_name="nutrition_order_encounter",
        null=True,
    )
    supporting_information = models.ManyToManyField(
        Reference, related_name="nutrition_order_supporting_information", blank=True
    )
    date_time = models.DateTimeField(null=True)
    orderer = models.ForeignKey(
        PractitionerPractitionerRoleReference,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_order_orderer",
        null=True,
    )
    performer = models.ManyToManyField(
        NutritionOrderPerformerReference,
        blank=True,
        related_name="nutrition_order_performer",
    )
    allergy_intolerance = models.ManyToManyField(
        "allergyintolerances.AllergyIntoleranceReference", blank=True
    )
    food_preference_modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="nutrition_order_food_preference_modifier",
        blank=True,
    )
    exclude_food_modifier = models.ManyToManyField(
        CodeableConcept,
        related_name="nutrition_order_exclude_food_modifier",
        blank=True,
    )
    outside_food_allowed = models.BooleanField(default=False)
    oral_diet = models.ForeignKey(
        NutritionOrderOralDiet,
        on_delete=models.SET_NULL,
        related_name="nutrition_order_oral_diet",
        null=True,
    )
    supplement = models.ManyToManyField(
        NutritionOrderSupplement,
        related_name="nutrition_order_supplement",
        blank=True,
    )
    enteral_formula = models.ForeignKey(
        NutritionOrderEnteralFormula,
        on_delete=models.SET_NULL,
        related_name="nutrition_order_enteral_formula",
        null=True,
    )
    additive = models.ManyToManyField(
        NutritionOrderAdditive, related_name="nutrition_order_additive", blank=True
    )
    note = models.ManyToManyField(
        Annotation, related_name="nutrition_order_note", blank=True
    )
