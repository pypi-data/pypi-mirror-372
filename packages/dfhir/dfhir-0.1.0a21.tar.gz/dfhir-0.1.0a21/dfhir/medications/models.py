"""medications app models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    OrganizationReference,
    Quantity,
    Ratio,
    TimeStampedModel,
)
from dfhir.medications.choices import MedicationStatus


class MedicationCodes(TimeStampedModel):
    """medication codes model."""

    code = models.CharField(null=True, max_length=255)
    display = models.CharField(max_length=255, null=True)


class MedicationDoseForm(TimeStampedModel):
    """medication dose form model."""

    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)


class MedicationIngredientItem(TimeStampedModel):
    """medication ingredient item model."""

    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)


class MedicationBatch(TimeStampedModel):
    """medication batch model."""

    lot_number = models.CharField(max_length=255, null=True)
    expiration_date = models.DateTimeField(null=True)


class MedicationSubstanceReference(BaseReference):
    """medication substance reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_substance_reference_identifier",
    )
    medication = models.ForeignKey(
        "Medication",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_substance_reference",
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_substance_reference_substance",
    )


class MedicationSubstanceCodeableReference(TimeStampedModel):
    """medication substance codeable reference model."""

    reference = models.ForeignKey(
        MedicationSubstanceReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_substance_codeable_reference_reference",
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_substance_codeable_reference_concept",
    )


class MedicationIngredient(TimeStampedModel):
    """medication ingredient model."""

    item = models.ForeignKey(
        MedicationSubstanceCodeableReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="mediation_ingredient_item",
    )
    is_active = models.BooleanField(default=True)
    strength_ratio = models.ForeignKey(
        Ratio,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="mediation_ingredient_strength_ratio",
    )
    strength_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="mediation_ingredient_strength_codeable_concept",
    )
    strength_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="mediation_ingredient_strength_quantity",
    )


class Medication(TimeStampedModel):
    """medication model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_identifier",
    )
    code = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="medication_code",
    )
    status = models.CharField(
        max_length=255, choices=MedicationStatus.choices, null=True
    )
    marketing_authorization_holder = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        related_name="medication_organization",
        null=True,
    )
    dose_form = models.OneToOneField(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_dose_form",
    )
    total_volume = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_total_volume",
    )
    ingredient = models.ManyToManyField(
        MedicationIngredient,
        blank=True,
        related_name="medication_ingredient",
    )
    batch = models.ForeignKey(
        MedicationBatch,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_batch",
    )
    definition = models.ForeignKey(
        "medicationknowledges.MedicationKnowledgeReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_definition",
    )


class MedicationReference(BaseReference):
    """medication reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_reference_identifier",
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_reference_medication",
    )


class MedicationCodeableReference(TimeStampedModel):
    """medication codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        MedicationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_codeable_reference_reference",
    )
