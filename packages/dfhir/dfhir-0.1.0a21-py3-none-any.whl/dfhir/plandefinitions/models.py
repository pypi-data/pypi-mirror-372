"""Plandefinitions models."""

from django.db import models

from dfhir.base.models import (
    Age,
    BaseReference,
    CodeableConcept,
    Coding,
    ContactDetail,
    Duration,
    Expression,
    Identifier,
    Period,
    Quantity,
    Range,
    Ratio,
    RelatedArtifact,
    TimeStampedModel,
    Timing,
    TriggerDefinition,
    UsageContext,
)

from . import choices


class PlanDefinitionGoalTarget(TimeStampedModel):
    """Plan Definition Goal Target model."""

    measure = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_goal_target_measure",
        null=True,
    )
    detail_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_goal_target_detail_quantity",
        null=True,
    )
    detail_range = models.ForeignKey(
        Range,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_goal_target_detail_range",
        null=True,
    )
    detail_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_goal_target_detail_codeable_concept",
        null=True,
    )
    detail_string = models.CharField(
        max_length=255,
        null=True,
    )
    detail_boolean = models.BooleanField(
        null=True,
    )
    detail_integer = models.IntegerField(
        null=True,
    )
    detail_ratio = models.ForeignKey(
        Ratio,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_goal_target_detail_ratio",
        null=True,
    )

    due = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_goal_target_due",
        null=True,
    )


class PlanDefinitionGoal(TimeStampedModel):
    """Plan Definition Goal model."""

    category = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_goal_category",
        null=True,
    )
    description = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_goal_description",
        null=True,
    )
    priority = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_goal_priority",
        null=True,
    )
    start = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_goal_start",
        null=True,
    )
    addresses = models.ManyToManyField(
        CodeableConcept,
        related_name="plan_definition_goal_addresses",
    )
    documentation = models.ManyToManyField(
        RelatedArtifact,
        related_name="plan_definition_goal_documentation",
    )
    target = models.ManyToManyField(
        PlanDefinitionGoalTarget,
        related_name="plan_definition_goal_target",
    )


class PlanDefinitionActorOptionTypeReferenceReference(BaseReference):
    """Plan Definition Actor Option Type Reference Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_identifier",
        null=True,
    )
    biologically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_biologically_derived_product",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_care_team",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_device",
        null=True,
    )
    device_definition = models.ForeignKey(
        "devicedefinitions.DeviceDefinition",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_device_definition",
        null=True,
    )
    endpoint = models.ForeignKey(
        "endpoints.Endpoint",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_endpoint",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_group",
        null=True,
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthCareService",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_healthcare_service",
        null=True,
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_location",
        null=True,
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_medication",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_organization",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_practitioner_role",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_related_person",
        null=True,
    )
    specimen = models.ForeignKey(
        "specimens.Specimen",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_specimen",
        null=True,
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.CASCADE,
        related_name="plan_definition_actor_option_type_reference_reference_substance",
        null=True,
    )


class PlanDefintionActorOption(TimeStampedModel):
    """Plan Definition Actor Option model."""

    type = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionParticipantType.choices,
        default=choices.PlanDefinitionActionParticipantType.PATIENT,
    )
    # type_canonical = models.ForeignKey(
    #     CapabilityStatementCanonical,
    #     on_delete=models.DO_NOTHING,
    #     related_name="plan_definition_actor_option_type_canonical",
    #     null=True,
    # )
    type_reference = models.ForeignKey(
        PlanDefinitionActorOptionTypeReferenceReference,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_actor_option_type_reference",
        null=True,
    )
    role = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_actor_option_role",
        null=True,
    )


class PlanDefinitionActor(TimeStampedModel):
    """Plan Definition Actor model."""

    title = models.CharField(
        max_length=255,
        null=True,
    )
    description = models.CharField(
        max_length=255,
        null=True,
    )
    option = models.ManyToManyField(
        PlanDefintionActorOption,
        related_name="plan_definition_actor_option",
    )


class PlanDefinitionActionCondition(TimeStampedModel):
    """Plan Definition Action Condition model."""

    kind = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionConditionKind.choices,
        default=choices.PlanDefinitionActionConditionKind.APPLICABILITY,
    )
    expression = models.ForeignKey(
        Expression,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_condition_expression",
        null=True,
    )


class PlanDefinitionActionInput(TimeStampedModel):
    """Plan Definition Action Input model."""

    title = models.CharField(
        max_length=255,
        null=True,
    )
    # requirement = models.ForeignKey(
    #     DataRequirement,
    #     on_delete=models.DO_NOTHING,
    #     related_name="plan_definition_action_input_requirement",
    #     null=True,
    # )
    related_data = models.CharField(
        max_length=255,
        null=True,
    )


class PlanDefinitionActionOutput(TimeStampedModel):
    """Plan Definition Action Output model."""

    title = models.CharField(
        max_length=255,
        null=True,
    )
    # requirement = models.ForeignKey(
    #     DataRequirement,
    #     on_delete=models.DO_NOTHING,
    #     related_name="plan_definition_action_output_requirement",
    #     null=True,
    # )
    related_data = models.CharField(
        max_length=255,
        null=True,
    )


class PlanDefinitionActionRelatedAction(TimeStampedModel):
    """Plan Definition Action Related Action model."""

    target_id = models.CharField(
        max_length=255,
        null=True,
    )

    relationship = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionRelatedActionRelationship.choices,
        default=choices.PlanDefinitionActionRelatedActionRelationship.BEFORE_START,
    )
    end_relationship = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionRelatedActionRelationship.choices,
        default=choices.PlanDefinitionActionRelatedActionRelationship.BEFORE_START,
    )
    offset_duration = models.ForeignKey(
        Duration,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_related_action_offset_duration",
        null=True,
    )
    offset_range = models.ForeignKey(
        Range,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_related_action_offset_range",
        null=True,
    )


class PlanDefinitionActionParticipant(TimeStampedModel):
    """Plan Definition Action Participant model."""

    type = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionParticipantType.choices,
        default=choices.PlanDefinitionActionParticipantType.PATIENT,
    )
    # type_canonical = models.ForeignKey(
    #     CapabilityStatementCanonical,
    #     on_delete=models.DO_NOTHING,
    #     related_name="plan_definition_action_participant_type_canonical",
    #     null=True,
    # )
    type_reference = models.ForeignKey(
        PlanDefinitionActorOptionTypeReferenceReference,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_participant_type_reference",
        null=True,
    )
    role = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_participant_role",
        null=True,
    )
    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_participant_function",
        null=True,
    )


class PlanDefinitionActionDynamicValue(TimeStampedModel):
    """Plan Definition Action Dynamic Value model."""

    path = models.CharField(
        max_length=255,
        null=True,
    )
    expression = models.ForeignKey(
        Expression,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_dynamic_value_expression",
        null=True,
    )


class PlanDefinitionSubjectReference(BaseReference):
    """Plan Definition Subject Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="plan_definition_subject_reference_identifier",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="plan_definition_subject_reference_group",
        null=True,
    )
    # medicinal_product_definition = models.ForeignKey(
    #     "medicinalproductdefinitions.MedicinalProductDefinition",
    #     on_delete=models.CASCADE,
    #     related_name="plan_definition_subject_reference_medicinal_product_definition",
    #     null=True,
    # )
    # substance_definition = models.ForeignKey(
    #     "substancedefinitions.SubstanceDefinition",
    #     on_delete=models.CASCADE,
    #     related_name="plan_definition_subject_reference_substance_definition",
    #     null=True,
    # )
    # adminstrable_product_definition = models.ForeignKey(
    #     "adminstrableproductdefinitions.AdminstrableProductDefinition",
    #     on_delete=models.CASCADE,
    #     related_name="plan_definition_subject_reference_adminstrable_product_definition",
    #     null=True,
    # )
    # manufactured_item_definition = models.ForeignKey(
    #     "manufactureditemdefinitions.ManufacturedItemDefinition",
    #     on_delete=models.CASCADE,
    #     related_name="plan_definition_subject_reference_manufactured_item_definition",
    #     null=True,
    # )
    # packaged_product_definition = models.ForeignKey(
    #     "packagedproductdefinitions.PackagedProductDefinition",
    #     on_delete=models.CASCADE,
    #     related_name="plan_definition_subject_reference_packaged_product_definition",
    #     null=True,
    # )


class PlanDefinitionAction(TimeStampedModel):
    """Plan Definition Action model."""

    link_id = models.CharField(
        max_length=255,
        null=True,
    )
    prefix = models.CharField(
        max_length=255,
        null=True,
    )
    title = models.CharField(
        max_length=255,
        null=True,
    )
    description = models.CharField(
        max_length=255,
        null=True,
    )
    text_equivalent = models.CharField(
        max_length=255,
        null=True,
    )
    priority = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionPriority.choices,
        default=choices.PlanDefinitionActionPriority.ROUTINE,
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="plan_definition_action_code",
        null=True,
    )
    reason = models.ManyToManyField(
        CodeableConcept,
        related_name="plan_definition_action_reason",
        blank=True,
    )
    documentation = models.ManyToManyField(
        RelatedArtifact,
        related_name="plan_definition_action_documentation",
        blank=True,
    )
    goal_id = models.CharField(
        max_length=255,
        null=True,
    )
    subject_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_subject_codeable_concept",
        null=True,
    )
    subject_reference = models.ForeignKey(
        "groups.GroupReference",
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_subject_reference",
        null=True,
    )
    # subject_canonical = models.ForeignKey(
    #     Canonical,
    #     on_delete=models.DO_NOTHING,
    #     related_name="plan_definition_action_subject_canonical",
    #     null=True,
    # )
    trigger = models.ManyToManyField(
        TriggerDefinition,
        related_name="plan_definition_action_trigger",
        blank=True,
    )
    condition = models.ManyToManyField(
        PlanDefinitionActionCondition,
        related_name="plan_definition_action_condition",
    )
    input = models.ManyToManyField(
        PlanDefinitionActionInput,
        related_name="plan_definition_action_input",
        blank=True,
    )
    output = models.ManyToManyField(
        PlanDefinitionActionOutput,
        related_name="plan_definition_action_output",
        blank=True,
    )
    related_action = models.ManyToManyField(
        PlanDefinitionActionRelatedAction,
        related_name="plan_definition_action_related_action",
        blank=True,
    )
    timing_age = models.ForeignKey(
        Age,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_timing_age",
        null=True,
    )
    timing_duration = models.ForeignKey(
        Duration,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_timing_duration",
        null=True,
    )
    timing_range = models.ForeignKey(
        Range,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_timing_range",
        null=True,
    )
    timing_timing = models.ForeignKey(
        Timing,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_timing_timing",
        null=True,
    )
    location = models.ForeignKey(
        "locations.LocationCodeableReference",
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_location",
        null=True,
    )
    participant = models.ManyToManyField(
        PlanDefinitionActionParticipant,
        related_name="plan_definition_action_participant",
        blank=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_action_type",
        null=True,
    )
    grouping_behavior = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionGroupingBehavior.choices,
        default=choices.PlanDefinitionActionGroupingBehavior.LOGICAL_GROUP,
    )
    selection_behavior = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionSelectionBehavior.choices,
        default=choices.PlanDefinitionActionSelectionBehavior.ALL,
    )
    required_behavior = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionRequiredBehavior.choices,
        default=choices.PlanDefinitionActionRequiredBehavior.MUST,
    )
    precheck_behavior = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionPrecheckBehavior.choices,
        default=choices.PlanDefinitionActionPrecheckBehavior.YES,
    )
    cardinality_behavior = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionActionCardinalityBehavior.choices,
        default=choices.PlanDefinitionActionCardinalityBehavior.SINGLE,
    )
    # definition_canonical = models.CharField(
    #     max_length=255,
    #     null=True,
    # )
    definition_uri = models.CharField(
        max_length=255,
        null=True,
    )
    # transform = models.ForeignKey(
    #     PlanDefinitionActionCanonicalMapStructure,
    #     on_delete=models.DO_NOTHING,
    #     related_name="plan_definition_action_transform",
    #     null=True,
    # )
    dynamic_value = models.ManyToManyField(
        PlanDefinitionActionDynamicValue,
        related_name="plan_definition_action_dynamic_value",
        blank=True,
    )
    action = models.ManyToManyField(
        "self",
        blank=True,
    )


class PlanDefinition(TimeStampedModel):
    """Plan Definition model."""

    url = models.URLField(
        null=True,
    )
    identifier = models.ManyToManyField(
        Identifier,
        related_name="plan_definition_identifier",
        blank=True,
    )
    version = models.CharField(
        max_length=255,
        null=True,
    )
    version_algorithm_string = models.CharField(
        max_length=255,
        null=True,
    )
    version_algorithm_coding = models.ForeignKey(
        Coding,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_version_algorithm_coding",
        null=True,
    )
    name = models.CharField(
        max_length=255,
        null=True,
    )
    title = models.CharField(
        max_length=255,
        null=True,
    )
    subtitle = models.CharField(
        max_length=255,
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_type",
        null=True,
    )
    status = models.CharField(
        max_length=255,
        choices=choices.PlanDefinitionStatus.choices,
        default=choices.PlanDefinitionStatus.ACTIVE,
    )
    experimental = models.BooleanField(
        default=False,
    )
    subject_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_subject_codeable_concept",
        null=True,
    )
    subject_reference = models.ForeignKey(
        PlanDefinitionSubjectReference,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_subject_reference",
        null=True,
    )
    # subject_canonical = models.ForeignKey(
    #     Canonical,
    #     on_delete=models.DO_NOTHING,
    #     related_name="plan_definition_subject_canonical",
    #     null=True,
    # )
    date = models.DateTimeField(
        null=True,
    )
    publisher = models.CharField(
        max_length=255,
        null=True,
    )
    contact = models.ManyToManyField(
        ContactDetail,
        related_name="plan_definition_contact",
        blank=True,
    )
    description = models.TextField(
        null=True,
    )
    use_context = models.ManyToManyField(
        UsageContext,
        related_name="plan_definition_use_context",
        blank=True,
    )
    jurisdiction = models.ManyToManyField(
        CodeableConcept,
        related_name="plan_definition_jurisdiction",
        blank=True,
    )
    purpose = models.TextField(
        null=True,
    )
    usage = models.TextField(
        null=True,
    )
    copyright = models.CharField(
        max_length=255,
        null=True,
    )
    copyright_label = models.CharField(
        max_length=255,
        null=True,
    )
    approval_date = models.DateField(
        null=True,
    )
    last_review_date = models.DateField(
        null=True,
    )
    effective_period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_effective_period",
        null=True,
    )
    topic = models.ManyToManyField(
        CodeableConcept,
        related_name="plan_definition_topic",
        blank=True,
    )
    author = models.ManyToManyField(
        ContactDetail,
        related_name="plan_definition_author",
        blank=True,
    )
    editor = models.ManyToManyField(
        ContactDetail,
        related_name="plan_definition_editor",
        blank=True,
    )
    reviewer = models.ManyToManyField(
        ContactDetail,
        related_name="plan_definition_reviewer",
        blank=True,
    )
    endorser = models.ManyToManyField(
        ContactDetail,
        related_name="plan_definition_endorser",
        blank=True,
    )
    related_artifact = models.ManyToManyField(
        RelatedArtifact,
        related_name="plan_definition_related_artifact",
        blank=True,
    )
    # library = models.ManyToManyField(
    #     CanonicalLibrary,
    #     related_name="plan_definition_library",
    #     blank=True,
    # )
    goal = models.ManyToManyField(
        PlanDefinitionGoal,
        related_name="plan_definition_goal",
        blank=True,
    )
    actor = models.ManyToManyField(
        PlanDefinitionActor,
        related_name="plan_definition_actor",
        blank=True,
    )
    action = models.ManyToManyField(
        PlanDefinitionAction,
        related_name="plan_definition_action",
        blank=True,
    )
    as_needed_boolean = models.BooleanField(
        null=True,
    )
    as_needed_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="plan_definition_as_needed_codeable_concept",
        null=True,
    )
