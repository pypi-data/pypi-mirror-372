"""Specimen definitions models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Coding,
    ContactDetail,
    Identifier,
    Period,
    Quantity,
    Range,
    TimeStampedModel,
    UsageContext,
)

from . import choices


class SpecimenDefinitionTypeTestedContainerAdditive(TimeStampedModel):
    """Specimen definition type tested container additive."""

    additive_codeable_concept = models.ForeignKey(
        CodeableConcept,
        related_name="specimen_definition_type_tested_container_additive_codeable_concept",
        on_delete=models.CASCADE,
        null=True,
    )
    # additive_reference = models.ForeignKey("substancedefinitions.SubstanceDefinitionReference", on_delete=models.CASCADE, related_name="specimen_definition_type_tested_container_additive_reference", null=True)
    preparation = models.TextField(null=True)


class SpecimenDefinitionTypeTestedContainer(TimeStampedModel):
    """Specimen definition type tested container."""

    material = models.ForeignKey(
        CodeableConcept,
        related_name="specimen_definition_type_tested_container_material",
        on_delete=models.CASCADE,
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        related_name="specimen_definition_type_tested_container_type",
        on_delete=models.CASCADE,
        null=True,
    )
    cap = models.ForeignKey(
        CodeableConcept,
        related_name="specimen_definition_type_tested_container_cap",
        on_delete=models.CASCADE,
        null=True,
    )
    description = models.TextField(null=True)
    capacity = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        null=True,
        related_name="specimen_definition_type_tested_container_capacity",
    )
    minimum_volume_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        null=True,
        related_name="specimen_definition_type_tested_container_minimum_volume_quantity",
    )
    minimum_volume_string = models.CharField(max_length=255, null=True)
    additive = models.ManyToManyField(
        SpecimenDefinitionTypeTestedContainerAdditive,
        related_name="specimen_definition_type_tested_container_additive",
        blank=True,
    )


class SpecimenDefinitionTypeTestedHandling(TimeStampedModel):
    """Specimen definition type tested handling."""

    temperature_qualifier = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="specimen_definition_type_tested_handling_temperature_qualifier",
        null=True,
    )
    temperature_range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        related_name="specimen_definition_type_tested_handling_temperature_range",
        null=True,
    )
    max_duration = models.ForeignKey(
        Quantity,
        on_delete=models.CASCADE,
        related_name="specimen_definition_type_tested_handling_max_duration",
        null=True,
    )
    instruction = models.TextField(null=True)


class SpecimenDefinitionTypeTested(TimeStampedModel):
    """Specimen definition type tested."""

    is_derived = models.BooleanField(null=True)
    type = models.ForeignKey(
        CodeableConcept,
        related_name="specimen_definition_type_tested_type",
        on_delete=models.CASCADE,
        null=True,
    )
    preference = models.CharField(
        max_length=255,
        choices=choices.SpecimenDefinitionTestedTypePreferenceChoices.choices,
        default=choices.SpecimenDefinitionTestedTypePreferenceChoices.PREFERRED,
    )
    container = models.ForeignKey(
        SpecimenDefinitionTypeTestedContainer,
        related_name="specimen_definition_type_tested_container",
        null=True,
        on_delete=models.CASCADE,
    )
    requirements = models.TextField(null=True)
    retention_time = models.ForeignKey(
        Quantity,
        related_name="specimen_definition_type_tested_retention_time",
        on_delete=models.CASCADE,
        null=True,
    )
    single_use = models.BooleanField(null=True)
    retention_criterion = models.ManyToManyField(
        CodeableConcept,
        related_name="specimen_definition_type_tested_retention_criterion",
        blank=True,
    )
    handling = models.ManyToManyField(
        SpecimenDefinitionTypeTestedHandling,
        related_name="specimen_definition_type_tested_handling",
        blank=True,
    )
    testing_destination = models.ManyToManyField(
        CodeableConcept,
        related_name="specimen_definition_type_tested_testing_destination",
        blank=True,
    )


class SpecimenDefinition(TimeStampedModel):
    """Specimen Definition model."""

    uri = models.URLField(null=True)
    identifier = models.ForeignKey(
        Identifier,
        related_name="specimen_definitions_identifier",
        null=True,
        on_delete=models.CASCADE,
    )
    version = models.CharField(max_length=255, null=True)
    version_algorithm_string = models.CharField(max_length=255, null=True)
    version_algorithm_coding = models.ForeignKey(
        Coding,
        related_name="specimen_definition_version_algorithm_coding",
        null=True,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255, null=True)
    # derived_from_canonical =
    derived_from_uri = ArrayField(models.URLField(), null=True)
    status = models.CharField(
        max_length=255,
        choices=choices.SpecimenDefinitionStatusChoices.choices,
        default=choices.SpecimenDefinitionStatusChoices.ACTIVE,
    )
    experimental = models.BooleanField(null=True)
    subject_codeable_concept = models.ForeignKey(
        CodeableConcept,
        related_name="specimen_definition_subject_codeable_concept",
        null=True,
        on_delete=models.CASCADE,
    )
    subject_reference = models.ForeignKey(
        "groups.GroupReference",
        related_name="specimen_definition_subject_reference",
        null=True,
        on_delete=models.CASCADE,
    )
    date = models.DateField(null=True)
    publisher = models.CharField(max_length=255, null=True)
    contact = models.ManyToManyField(
        ContactDetail, related_name="specimen_definition_contact", blank=True
    )
    description = models.TextField(null=True)
    use_context = models.ManyToManyField(
        UsageContext, related_name="specimen_definition_use_context", blank=True
    )
    jurisdiction = models.ManyToManyField(
        CodeableConcept, related_name="specimen_definition_jurisdiction", blank=True
    )
    purpose = models.TextField(null=True)
    copyright = models.TextField(null=True)
    copyright_label = models.CharField(max_length=255, null=True)
    approval_date = models.DateField(null=True)
    last_review_date = models.DateField(null=True)
    effective_period = models.ForeignKey(
        Period,
        related_name="specimen_definition_effective_period",
        on_delete=models.CASCADE,
        null=True,
    )
    type_collected = models.ForeignKey(
        CodeableConcept,
        related_name="specimen_definition_type_collected",
        on_delete=models.CASCADE,
        null=True,
    )
    patient_preparation = models.ManyToManyField(
        CodeableConcept,
        related_name="specimen_definition_patient_preparation",
        blank=True,
    )
    time_aspect = models.CharField(max_length=255, null=True)
    collection = models.ManyToManyField(
        CodeableConcept, related_name="specimen_definition_collection", blank=True
    )
    type_tested = models.ManyToManyField(
        SpecimenDefinitionTypeTested,
        related_name="specimen_definition_type_tested",
        blank=True,
    )


class SpecimenDefinitionReference(BaseReference):
    """Specimen Definition Reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        null=True,
        related_name="specimen_definition_reference_identifier",
    )
    specimen_definition = models.ForeignKey(
        SpecimenDefinition,
        on_delete=models.CASCADE,
        null=True,
        related_name="specimen_definition_reference_specimen_definition",
    )
