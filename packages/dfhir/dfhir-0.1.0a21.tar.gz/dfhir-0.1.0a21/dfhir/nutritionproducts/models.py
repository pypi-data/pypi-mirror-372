"""Nutrition Products models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    Attachment,
    BaseReference,
    CodeableConcept,
    Identifier,
    OrganizationReference,
    Quantity,
    Ratio,
    TimeStampedModel,
)

from . import choices


class NutritionProductNutrients(TimeStampedModel):
    """Nutrition Product Nutrients model."""

    item = models.ForeignKey(
        "substances.SubstanceCodeableReference",
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_nutrients_item",
        null=True,
    )
    amount_ratio = models.ForeignKey(
        Ratio,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_nutrients_amount_ratio",
        null=True,
    )
    amount_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_nutrients_amount_quantity",
        null=True,
    )


class NutritionProductCharacteristic(TimeStampedModel):
    """Nutrition Product Characteristic model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_characteristic_type",
        null=True,
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_characteristic_value_codeable_concept",
        null=True,
    )
    value_string = models.CharField(max_length=255, null=True)
    value_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_characteristic_value_quantity",
        null=True,
    )
    value_boolean = models.BooleanField(null=True)
    value_base64_binary = models.TextField(null=True)
    value_attachment = models.ForeignKey(
        Attachment,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_characteristic_value_attachment",
        null=True,
    )


class NutritionProductInstance(TimeStampedModel):
    """Nutrition Product Instance model."""

    quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_instance_quantity",
        null=True,
    )
    identifier = models.ManyToManyField(
        Identifier, related_name="nutrition_product_instance_identifier", blank=True
    )
    name = models.CharField(max_length=255, null=True)
    lot_number = models.CharField(max_length=255, null=True)
    expiry = models.DateTimeField(null=True)
    use_by = models.DateTimeField(null=True)
    biological_source_event = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_instance_biological_source_event",
        null=True,
    )


class NutritionProductIngredient(TimeStampedModel):
    """Nutrition Product Ingredient model."""

    item = models.ForeignKey(
        "NutritionProductCodeableReference",
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_ingredient_item",
        null=True,
    )
    amount_ratio = models.ForeignKey(
        Ratio,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_ingredient_amount_ratio",
        null=True,
    )
    amount_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_ingredient_amount_quantity",
        null=True,
    )
    allergen = models.BooleanField(null=True)


class NutritionProductReference(BaseReference):
    """Nutrition Product Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_reference_identifier",
        null=True,
    )
    nutrition_product = models.ForeignKey(
        "NutritionProduct",
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_reference_product",
        null=True,
    )


class NutritionProductCodeableReference(TimeStampedModel):
    """Nutrition Product Codeable Reference model."""

    reference = models.ForeignKey(
        NutritionProductReference,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_codeable_reference_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_codeable_reference_concept",
        null=True,
    )


class NutritionProduct(TimeStampedModel):
    """Nutrition Product model."""

    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_code",
        null=True,
    )
    status = models.CharField(
        max_length=255, choices=choices.NutritionProductStatusChoices.choices, null=True
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="nutrition_product_category", blank=True
    )

    manufacturer = models.ManyToManyField(
        OrganizationReference,
        related_name="nutrition_product_manufacturer",
        blank=True,
    )
    nutrient = models.ManyToManyField(
        NutritionProductNutrients, related_name="nutrition_product_nutrient", blank=True
    )
    ingredient_summary = models.TextField(null=True)
    ingredient = models.ManyToManyField(
        NutritionProductIngredient,
        related_name="nutrition_product_ingredient",
        blank=True,
    )
    energy = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="nutrition_product_energy",
        null=True,
    )
    characteristic = models.ManyToManyField(
        NutritionProductCharacteristic,
        related_name="nutrition_product_characteristic",
        blank=True,
    )
    instance = models.ManyToManyField(
        NutritionProductInstance, related_name="nutrition_product_instance", blank=True
    )
    note = models.ManyToManyField(
        Annotation, related_name="nutrition_product_note", blank=True
    )
