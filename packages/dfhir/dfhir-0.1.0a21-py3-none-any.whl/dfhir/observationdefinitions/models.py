"""observation definitions models."""

from django.db import models

from dfhir.base.models import BaseReference, Identifier, TimeStampedModel

from .choices import (
    ObservationDefinitionPermittedDataTypeChoices,
    ObservationDefinitionStatusChoices,
    QualifiedValueGenderChoices,
    QualifiedValueRangeCategoryChoices,
)


class ObservationDefinitionQualifiedValue(TimeStampedModel):
    """observation definition quality value model."""

    context = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_qualified_value_context",
    )
    applies_to = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_qualified_value_applies_to",
    )
    gender = models.CharField(
        max_length=255, null=True, choices=QualifiedValueGenderChoices.choices
    )
    age = models.ForeignKey(
        "base.Range",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_qualified_value_age",
    )
    gestational_age = models.ForeignKey(
        "base.Range",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_qualified_value_gestational_age",
    )
    condition = models.CharField(max_length=255, null=True)
    range_category = models.CharField(
        max_length=255, null=True, choices=QualifiedValueRangeCategoryChoices.choices
    )
    range = models.ForeignKey(
        "base.Range",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_qualified_value_range",
    )
    # TODO: valid_coded_valueset = models.ForeignKey(
    #     "Valueset", on_delete=models.SET_NULL, null=True
    # )
    # TODO: normal_coded_valueset = models.ForeignKey(
    #     "Valueset", on_delete=models.SET_NULL, null=True
    # )
    # TODO: abnormal_coded_valueset = models.ForeignKey(
    #     "Valueset", on_delete=models.SET_NULL, null=True
    # )
    # TODO: critical_coded_valueset = models.ForeignKey(
    #     "Valueset", null=True, on_delete=models.SET_NULL
    # )
    interpretation = models.ManyToManyField(
        "base.CodeableConcept",
        blank=True,
        related_name="observation_definition_qualified_value_interpretation",
    )


class ObservationDefinitionComponent(TimeStampedModel):
    """observation definition component model."""

    code = models.ForeignKey(
        "base.CodeableConcept", null=True, on_delete=models.SET_NULL
    )
    permitted_data_type = models.CharField(
        max_length=255,
        null=True,
        choices=ObservationDefinitionPermittedDataTypeChoices.choices,
    )
    permitted_unit = models.ManyToManyField(
        "base.Coding",
        blank=True,
        related_name="observation_definition_component_permitted_unit",
    )
    qulaified_value = models.ManyToManyField(
        ObservationDefinitionQualifiedValue,
        blank=True,
        related_name="observation_definition_component_qualified_value",
    )


class ObservationDefinitionQuestionnaireReference(BaseReference):
    """observation definition questionnaire reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_questionnaire_reference_identifier",
    )
    # TODO: questionnaire = models.ForeignKey(
    #     "questionnaires.Questionnaire",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     related_name="observation_definition_questionnaire_reference_questionnaire",
    # )
    observatoin_definition = models.ForeignKey(
        "ObservationDefinition",
        on_delete=models.SET_NULL,
        null=True,
    )


class ObservationDefinition(TimeStampedModel):
    """observation definition model."""

    url = models.URLField(null=True)
    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_identifier",
    )
    version = models.CharField(max_length=255, null=True)
    version_algorithm_string = models.CharField(max_length=255, null=True)
    version_algorithm_coding = models.ForeignKey(
        "base.Coding",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_version_algorithm_coding",
    )
    name = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255, null=True)
    status = models.CharField(
        max_length=255, null=True, choices=ObservationDefinitionStatusChoices.choices
    )
    experimental = models.BooleanField(default=False)
    date = models.DateTimeField(null=True)
    publisher = models.CharField(max_length=255, null=True)
    contact = models.ManyToManyField(
        "base.ContactDetail", blank=True, related_name="observation_definition_contact"
    )
    description = models.TextField(null=True)
    use_context = models.ManyToManyField(
        "base.UsageContext",
        blank=True,
        related_name="observation_definition_use_context",
    )
    jurisdiction = models.ManyToManyField(
        "base.CodeableConcept",
        blank=True,
        related_name="observation_definition_jurisdiction",
    )
    purpose = models.TextField(null=True)
    copyright = models.TextField(null=True)
    copyright_label = models.CharField(max_length=255, null=True)
    approval_date = models.DateTimeField(null=True)
    last_review_date = models.DateTimeField(null=True)
    effective_period = models.ForeignKey(
        "base.Period",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_effective_period",
    )
    # TODO: derived_from_canonical = models.ManyToManyField("ObservationDefinition", blank=True)
    derived_from_uri = models.URLField(null=True)
    subject = models.ManyToManyField(
        "base.CodeableConcept",
        blank=True,
        related_name="observation_definition_subject",
    )
    performer_type = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_performer_type",
    )
    category = models.ManyToManyField(
        "base.CodeableConcept",
        blank=True,
        related_name="observation_definition_category",
    )
    code = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_code",
    )
    permitted_data_type = models.CharField(
        max_length=255,
        null=True,
        choices=ObservationDefinitionPermittedDataTypeChoices.choices,
    )
    multiple_results_allowed = models.BooleanField(default=False)
    body_site = models.ManyToManyField(
        "base.CodeableConcept",
        blank=True,
        related_name="observation_definition_body_site",
    )
    method = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_method",
    )
    specimen = models.ForeignKey(
        "specimendefinitions.SpecimenDefinition",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_specimen",
    )
    device = models.ForeignKey(
        "devicedefinitions.DeviceDefinition",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_device",
    )
    preferred_report_name = models.CharField(max_length=255, null=True)
    permitted_unit = models.ManyToManyField(
        "base.Coding",
        blank=True,
        related_name="observation_definition_permitted_unit",
    )
    qualified_value = models.ManyToManyField(
        ObservationDefinitionQualifiedValue,
        related_name="observation_definition_qualified_value",
        blank=True,
    )
    has_member = models.ManyToManyField(
        ObservationDefinitionQuestionnaireReference,
        blank=True,
        related_name="observation_definition_has_member",
    )
    component = models.ManyToManyField(
        ObservationDefinitionComponent,
        blank=True,
        related_name="observation_definition_component",
    )


class ObservationDefinitionReference(BaseReference):
    """observation definition reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_reference_identifier",
    )
    observation_definition = models.ForeignKey(
        "ObservationDefinition",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_definition_reference_observation_definition",
    )
