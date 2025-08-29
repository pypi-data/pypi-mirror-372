"""Substances models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Ratio,
    TimeStampedModel,
)

from . import choices


class SubstanceIngredient(TimeStampedModel):
    """Substance Ingredient model."""

    quantity = models.ForeignKey(
        Ratio, related_name="substance_ingredient_quantity", on_delete=models.CASCADE
    )
    substance_codeable_concept = models.ForeignKey(
        CodeableConcept,
        related_name="substance_ingredient_substance",
        on_delete=models.CASCADE,
        null=True,
    )
    substance_reference = models.ForeignKey(
        "SubstanceReference",
        related_name="substance_ingredient_substance_reference",
        on_delete=models.CASCADE,
        null=True,
    )


class Substance(TimeStampedModel):
    """Substance model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="substances_identifier", blank=True
    )
    status = models.CharField(
        max_length=255, null=True, choices=choices.SubstanceStatusChoices.choices
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="substances_category", blank=True
    )
    # TODO: this should reference substanceDeefintionCodeableReference
    # code = models.ForeignKey(
    #     CodeableConcept, related_name="substances_code", on_delete=models.CASCADE
    # )
    description = models.TextField(null=True)
    expiry = models.DateTimeField(null=True)
    ingredient = models.ManyToManyField(
        SubstanceIngredient,
        related_name="substances_ingredient",
        blank=True,
    )


class SubstanceReference(BaseReference):
    """Substance Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="substance_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    substance = models.ForeignKey(
        Substance,
        related_name="substance_reference_substance",
        on_delete=models.CASCADE,
        null=True,
    )


class SubstanceCodeableReference(TimeStampedModel):
    """Substance Codeable Reference model."""

    reference = models.ForeignKey(
        SubstanceReference,
        on_delete=models.CASCADE,
        null=True,
        related_name="substance_codeable_reference_reference",
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="substance_codeable_reference_concept",
    )
