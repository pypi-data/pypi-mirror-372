"""Medication Knowledge models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Period,
    TimeStampedModel,
)
from dfhir.medicationknowledges.choices import MedicationKnowledgeStatusChoices


class MedicationKnowledgeReference(BaseReference):
    """Medication Knowledge Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_reference_identifier",
    )
    medication_knowledge = models.ForeignKey(
        "MedicationKnowledge",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_reference_medication_knowledge",
    )


class MedicationKnowledgeRelatedMedicationKnowledge(TimeStampedModel):
    """Medication Knowledge Related Medication Knowledge model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_related_medication_knowledge_type",
    )
    reference = models.ForeignKey(
        MedicationKnowledgeReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_related_medication_knowledge_reference",
    )


class MedicationKnowledgeMonograph(TimeStampedModel):
    """Medication Knowledge Monograph model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_monograph_type",
    )
    source = models.ForeignKey(
        "documentreferences.DocumentReferenceReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_monograph_source",
    )


class MedicationKnowledgeCost(TimeStampedModel):
    """medication knowledge cost model."""

    effective_date = models.ManyToManyField(
        Period, blank=True, related_name="medication_knowledge_cost_effective_date"
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_cost_type",
    )
    source = models.CharField(max_length=255, null=True)
    cost_money = models.ForeignKey(
        "base.Money",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_cost_cost_money",
    )
    cost_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_cost_cost_codeable_concept",
    )


class MedicationKnowledgeMonitoringProgram(TimeStampedModel):
    """Medication Knowledge Monitoring Program model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_monitoring_program_type",
    )
    name = models.CharField(max_length=255, null=True)


class MedicationKnowledgePatientCharacteristics(TimeStampedModel):
    """medication knowledge dosing guideline treatment intent dosage patient characteristics model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="med_knowledge_dosing_guideline_treatment_intent_dosage_patient_characteristics_type",
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="med_knowledge_dosing_guideline_treatment_intent_dosage_patient_characteristics_value_codeable_concept",
    )
    value_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="med_knowledge_dosing_guideline_treatment_intent_dosage_patient_characteristics_value_quantity",
    )
    value_range = models.ForeignKey(
        "base.Range",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="med_knowledge_dosing_guideline_treatment_intent_dosage_patient_characteristics_value_range",
    )


class MedicationKnowledgeIndicationGuidelineDosingGuidelineDosage(TimeStampedModel):
    """medication knowledge dosing guideline treatment intent dosage model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_dosing_guideline_dosage_type",
    )
    # TODO: dosage = models.ForeignKey(
    #     "Dosage",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="medication_knowledge_dosing_guideline_dosage_dose_quantity",
    # )


class MedicationKnowledgeIndicationGuidelineDosingGuideline(TimeStampedModel):
    """medication knowledge dosing guideline model."""

    treatment_intent = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_dosing_guideline_treatment_intent",
    )
    dosage = models.ManyToManyField(
        MedicationKnowledgeIndicationGuidelineDosingGuidelineDosage,
        blank=True,
        related_name="medication_knowledge_dosing_guideline_dose",
    )
    administration_treatment = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_dosing_guideline_administration_treatment",
    )
    patient_characteristics = models.ManyToManyField(
        MedicationKnowledgePatientCharacteristics,
        blank=True,
        related_name="medication_knowledge_dosing_guideline_patient_characteristics",
    )


class MedicationKnowledgeIndicationGuideline(TimeStampedModel):
    """medication knowledge indication guideline model."""

    # TODO: indication = models.ManyToManyField(
    #     "ClinicalUseDefinition",
    #     blank=True,
    #     related_name="medication_knowledge_indication_guidline_indication",
    # )
    dosing_guideline = models.ManyToManyField(
        MedicationKnowledgeIndicationGuidelineDosingGuideline,
        blank=True,
        related_name="medication_knowledge_indication_guidline_dosing_guideline",
    )


class MedicationKnowledgeMedicineClassification(TimeStampedModel):
    """medication knowledge medicine classification model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_medicine_classification_type",
    )
    source_string = models.CharField(max_length=255, null=True)
    source_uri = models.URLField(null=True)
    classification = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="medication_knowledge_medicine_classification_classification",
    )


class MedicationKnowledgePackaging(TimeStampedModel):
    """medication knowledge packaging model."""

    cost = models.ForeignKey(
        MedicationKnowledgeCost,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_packaging_cost",
    )
    # TODO: pockage_product = models.ForeignKey(
    #     "PackageProductDefinitionReference", on_delete=models.DO_NOTHING, null=True
    # )


class MedicationKnowledgeStorageGuidelineEnvironmentalSetting(TimeStampedModel):
    """medication knowledge storage guideline environmental setting model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
    )
    value_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="storage_guideline_environmental_setting_value_quantity",
    )
    value_range = models.ForeignKey(
        "base.Range",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="storage_guideline_environmental_setting_value_range",
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="storage_guideline_environmental_setting_value_codeable_concept",
    )


class MedicationKnowledgeStorageGuideline(TimeStampedModel):
    """medication knowledge storage guideline model."""

    reference = models.URLField(null=True)
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="storage_guideline_note"
    )
    stability_duration = models.ForeignKey(
        "base.Duration",
        on_delete=models.DO_NOTHING,
        related_name="storage_guideline_stability_duration",
        null=True,
    )
    environmental_setting = models.ManyToManyField(
        MedicationKnowledgeStorageGuidelineEnvironmentalSetting,
        blank=True,
        related_name="storage_guideline_environmental_setting",
    )


class MedicationKnowledgeRegulatorySubstitution(TimeStampedModel):
    """Medication Knowledge Regulatory Substitution model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="regulatory_substitution_type",
    )
    allowed = models.BooleanField(null=True)


class MedicationKnowledgeRegulatoryMaxDispense(TimeStampedModel):
    """Medication Knowledge Regulatory Max Dispense model."""

    quantity = models.ForeignKey(
        "base.SimpleQuantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="regulatory_max_dispense_quantity",
    )
    period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="regulatory_max_dispense_period",
    )


class MedicationKnowledgeRegulatory(TimeStampedModel):
    """Medication Knowledge Regulatory model."""

    regulatory_authority = models.ForeignKey(
        "base.OrganizationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="regulatory_authority",
    )
    substitution = models.ManyToManyField(
        MedicationKnowledgeRegulatorySubstitution,
        blank=True,
        related_name="regulatory_substitution",
    )
    schedule = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="medication_knowledge_schedule"
    )
    max_dispense = models.ManyToManyField(
        MedicationKnowledgeRegulatoryMaxDispense,
        blank=True,
        related_name="regulatory_max_dispense",
    )


class MedicationKnowledgeDefinitionalIngredient(TimeStampedModel):
    """Medication Knowledge Definitional Ingredient model."""

    item = models.ForeignKey(
        "substances.SubstanceCodeableReference",
        on_delete=models.DO_NOTHING,
        related_name="medication_knowledge_definitional_ingredient_item",
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        related_name="medication_knowledge_definitional_ingredient_type",
        null=True,
        on_delete=models.DO_NOTHING,
    )
    strength_ratio = models.ForeignKey(
        "base.Ratio",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_definitional_ingredient_strength_ratio",
    )
    strength_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_definitional_ingredient_strength_quantity",
    )
    strength_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_definitional_ingredient_strength_codeable_concept",
    )


class MedicationKnowledgeDefinitionalDrugCharacteristic(TimeStampedModel):
    """medication knowledge definitional drug characteristic model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_definitional_drug_characteristic_type",
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_definitional_drug_characteristic_value_codeable_concept",
    )
    value_string = models.CharField(max_length=255, null=True)
    value_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_definitional_drug_characteristic_value_quantity",
    )
    value_base_64_binary = models.TextField(null=True)
    value_attachment = models.ForeignKey(
        "base.Attachment",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_definitional_drug_characteristic_value_attachment",
    )


class MedicationKnowledgeDefinitional(TimeStampedModel):
    """medication knowledge definitional model."""

    # TODO: definition = models.ManyToManyField(
    #     "MedicationalProductDefinitionReference",
    #     blank=True,
    #     related_name="medication_knowledge_definitional_definition",
    # )
    dose_form = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_knowledge_definitional_dose_form",
    )
    intended_route = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="medication_knowledge_definitional_intended_route",
    )
    ingredient = models.ManyToManyField(
        MedicationKnowledgeDefinitionalIngredient,
        blank=True,
        related_name="medication_knowledge_definitional_ingredient",
    )
    drug_characteristic = models.ManyToManyField(
        MedicationKnowledgeDefinitionalDrugCharacteristic,
        blank=True,
        related_name="medication_knowledge_definitional_drug_chracteristic",
    )


class MedicationKnowledge(TimeStampedModel):
    """medication knowledge model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="medication_knowledge_identifier"
    )
    code = models.ForeignKey(
        CodeableConcept,
        null=True,
        related_name="medication_knowledge_code",
        on_delete=models.DO_NOTHING,
    )
    status = models.CharField(
        max_length=255, null=True, choices=MedicationKnowledgeStatusChoices.choices
    )
    author = models.ForeignKey(
        "base.ContactDetail",
        null=True,
        related_name="medication_knowledge_author",
        on_delete=models.DO_NOTHING,
    )
    jurisdiction = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="medication_knowledge_jurisdiction"
    )
    name = models.CharField(max_length=255, null=True)
    related_medication_knowledge = models.ManyToManyField(
        MedicationKnowledgeRelatedMedicationKnowledge,
        blank=True,
        related_name="medication_knowledge_related_medication_knowledge",
    )
    associate_medication = models.ManyToManyField(
        "medications.MedicationReference",
        blank=True,
        related_name="medication_knowledge_associate_medication",
    )
    product_type = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="medication_knowledge_product_type",
    )
    monograph = models.ManyToManyField(
        MedicationKnowledgeMonograph,
        blank=True,
        related_name="medication_knowledge_monograph",
    )
    preparation_instruction = models.TextField(null=True)
    cost = models.ManyToManyField(
        MedicationKnowledgeCost, blank=True, related_name="medication_knowledge_cost"
    )
    monitoring_program = models.ManyToManyField(
        MedicationKnowledgeMonitoringProgram,
        blank=True,
        related_name="medication_knowledge_monitoring_program",
    )
    indication_guideline = models.ManyToManyField(
        MedicationKnowledgeIndicationGuideline,
        blank=True,
        related_name="medication_knowledge_indication_guideline",
    )
    medicine_classification = models.ManyToManyField(
        MedicationKnowledgeMedicineClassification,
        blank=True,
        related_name="medication_knowledge_medicine_classification",
    )
    packaging = models.ManyToManyField(
        MedicationKnowledgePackaging,
        blank=True,
        related_name="medication_knowledge_packaging",
    )
    # TODO: clinical_use_issue = models.ManyToManyField("ClinicalUseIssueReference")
    storage_guideline = models.ManyToManyField(
        MedicationKnowledgeStorageGuideline,
        blank=True,
        related_name="medication_knowledge_storage_guideline",
    )
    regulatory = models.ManyToManyField(
        MedicationKnowledgeRegulatory,
        blank=True,
        related_name="medication_knowledge_regulatory",
    )
    definitional = models.ForeignKey(
        MedicationKnowledgeDefinitional,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="medication_knowledge_definitional",
    )
