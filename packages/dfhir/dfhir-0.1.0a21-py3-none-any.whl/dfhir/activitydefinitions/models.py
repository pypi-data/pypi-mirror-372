"""activity definition models."""

from django.db import models

from dfhir.activitydefinitions.choices import (
    ActivityDefinitionIntentChoices,
    ActivityDefinitionKindChoices,
    ActivityDefinitionParticipantTypeChoices,
    ActivityDefinitionPriorityChoices,
    ActivityDefinitionStatus,
)
from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)


class ActivityDefinitionParticipantTypeReference(BaseReference):
    """activity definition participant type reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_identifier",
    )
    biologically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_biologically_derived_product_reference_biologically_derived_product",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_practitioner_type_reference_care_plan",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_device_reference_idevice",
    )
    device_definition = models.ForeignKey(
        "devicedefinitions.DeviceDefinition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_device_definition_reference_device_definition",
    )
    endpoint = models.ForeignKey(
        "endpoints.Endpoint",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_endpoint",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_group",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_healthcare_service",
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_location",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_medication",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_organization",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_patient",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_practitioner_type_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_practitioner_type_reference_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_related_person",
    )
    specimen = models.ForeignKey(
        "specimens.Specimen",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_specimen",
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference_substance",
    )


class ActivityDefinitionParticipant(TimeStampedModel):
    """activity definition participant model."""

    type = models.CharField(
        max_length=255,
        choices=ActivityDefinitionParticipantTypeChoices.choices,
        null=True,
    )
    # TODO: type_canonical = models.ForeignKey(
    #     "CapabilityStatementCanonical",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="activity_definition_participant",
    # )
    type_reference = models.ForeignKey(
        ActivityDefinitionParticipantTypeReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_type_reference",
    )
    role = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_role",
    )
    function = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_participant_function",
    )


class ActivityDefinitionProductProductReference(BaseReference):
    """activity definition product reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_product_product_reference_identifier",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_product_product_reference_medication",
    )
    # TODO: ingredient = models.ForeignKey(
    #     "ingredients.Ingredient",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="activity_definition_product_reference_ingredient",
    # )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_product_product_reference_substance",
    )
    # TODO: substance_definition = models.ForeignKey(
    #     "substancedefinitions.SubstanceDefinition",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="activity_definition_product_product_reference_substance_definition",
    # )


class ActivityDefinitionSubjectReference(BaseReference):
    """activity definition subject reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_subject_reference_identifier",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_subject_reference_group",
    )
    # TODO: medicinal_product_definition = models.ForeignKey(
    #     "medicinalproductdefinitions.MedicinalProductDefinition",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="activity_definition_subject_reference_medicinal_product_definition",
    # )

    # TODO: substance_definition = models.ForeignKey(
    #     "substancedefinitions.SubstanceDefinition",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="activity_definition_subject_reference_substance_definition",
    # )

    # TODO: administrable_product_definition = models.ForeignKey(
    #     "administrableproductdefinitions.AdministrableProductDefinition",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="activity_definition_administrable_product_definition_reference_identifier",
    # )

    # TODO: manufactured_item_definition = models.ForeignKey(
    #     "manufactureditemdefinitions.ManufacturedItemDefinition",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="activity_definition_manufactured_item_definition_reference_identifier",
    # )

    # TODO: packaged_product_definition = models.ForeignKey(
    #     "packagedproductdefinitions.PackagedProductDefinition",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="activity_definition_packaged_product_definition_reference_identifier",
    # )


class ActivityDefinitionDynamicValue(TimeStampedModel):
    """activity definition dynamic value model."""

    path = models.CharField(max_length=255, null=True)
    expression = models.ForeignKey(
        "base.Expression",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_dynamic_value_expression",
    )


class ActivityDefinition(TimeStampedModel):
    """activity definition model."""

    url = models.URLField(null=True)
    identifier = models.ManyToManyField(
        Identifier, related_name="activity_definition_identifier", blank=True
    )
    version = models.CharField(max_length=255, null=True)
    version_algorithm_string = models.CharField(max_length=255, null=True)
    version_algorithm_coding = models.ForeignKey(
        "base.Coding",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_version_algorithm_coding",
        null=True,
    )
    name = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255, null=True)
    subtitle = models.CharField(max_length=255, null=True)
    status = models.CharField(
        max_length=255, null=True, choices=ActivityDefinitionStatus.choices
    )
    experimental = models.BooleanField(null=True)
    subject_codealbe_concept = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_subject_codeable_concept",
        null=True,
    )
    subject_reference = models.ForeignKey(
        ActivityDefinitionSubjectReference,
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_subject_reference",
        null=True,
    )
    # TODO: subject_canonical = models.ForeignKey(
    #     "EvidenceVariable",
    #     on_delete=models.DO_NOTHING,
    #     related_name="activity_definition_subject_canonical",
    #     null=True,
    # )
    date = models.DateTimeField(null=True)
    publisher = models.CharField(max_length=255, null=True)
    contact = models.ManyToManyField(
        "base.ContactDetail", related_name="activity_definition_contact", blank=True
    )
    description = models.TextField(null=True)
    use_context = models.ManyToManyField(
        "base.UsageContext", related_name="activity_definition_use_context", blank=True
    )
    jurisdiction = models.ManyToManyField(
        "base.CodeableConcept",
        related_name="activity_definition_jurisdiction",
        blank=True,
    )
    purpose = models.TextField(null=True)
    usage = models.TextField(null=True)
    copyright = models.TextField(null=True)
    copyright_label = models.TextField(null=True)
    approval_date = models.DateField(null=True)
    last_review_date = models.DateField(null=True)
    effective_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_period",
        null=True,
    )
    topic = models.ManyToManyField(
        "base.CodeableConcept", related_name="activity_definition_topic", blank=True
    )
    author = models.ManyToManyField(
        "base.ContactDetail", related_name="activity_definition_author", blank=True
    )
    editor = models.ManyToManyField(
        "base.ContactDetail", related_name="activity_definition_editor", blank=True
    )
    reviewer = models.ManyToManyField(
        "base.ContactDetail", related_name="activity_definition_reviewer", blank=True
    )
    endorser = models.ManyToManyField(
        "base.ContactDetail", related_name="activity_definition_endorser", blank=True
    )
    related_artifact = models.ManyToManyField(
        "base.RelatedArtifact",
        related_name="activity_definition_related_artifact",
        blank=True,
    )

    # TODO: library = models.ManyToManyField(
    #     "CanonicalLibrary", related_name="activity_definition_library", blank=True
    # )
    kind = models.CharField(
        max_length=255, null=True, choices=ActivityDefinitionKindChoices.choices
    )
    # TODO: profile = models.ForeignKey(
    #     "StructuredDefinitionCanonical",
    #     on_delete=models.DO_NOTHING,
    #     related_name="activity_definition_profile",
    #     null=True,
    # )
    code = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_code",
        null=True,
    )
    intent = models.CharField(
        max_length=255, null=True, choices=ActivityDefinitionIntentChoices.choices
    )
    priority = models.CharField(
        max_length=255, null=True, choices=ActivityDefinitionPriorityChoices.choices
    )
    do_not_perform = models.BooleanField(null=True)
    timing_timing = models.ForeignKey(
        "base.Timing",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_timing_timing",
        null=True,
    )
    timing_age = models.ForeignKey(
        "base.Age",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_timing_age",
        null=True,
    )
    timing_range = models.ForeignKey(
        "base.Range",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_timing_range",
        null=True,
    )
    timing_duration = models.ForeignKey(
        "base.Duration",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_timing_duration",
        null=True,
    )
    as_needed_boolean = models.BooleanField(null=True)
    as_needed_codeable_concept = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_as_needed_codeable_concept",
        null=True,
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_location",
        null=True,
    )
    participant = models.ManyToManyField(
        ActivityDefinitionParticipant,
        related_name="activity_definition_participant",
        blank=True,
    )
    product_reference = models.ForeignKey(
        ActivityDefinitionProductProductReference,
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_product_reference",
        null=True,
    )
    product_codeable_concept = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_product_codeable_concept",
        null=True,
    )
    quantity = models.ForeignKey(
        "base.SimpleQuantity",
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_quantity",
        null=True,
    )
    # TODO: dosage = models.ManyToManyField(
    #     "base.Dosage",
    #     related_name="activity_definition_dosage",
    #     blank=True,
    # )
    body_site = models.ManyToManyField(
        "base.CodeableConcept", related_name="activity_definition_body_site", blank=True
    )
    # TODO: subject_requirements = models.ForeignKey(
    #     "SpecimenDefinitionCanonical",
    #     on_delete=models.DO_NOTHING,
    #     related_name="activity_definition_subject_reference",
    #     null=True,
    # )

    # TODO: observation_requirement = models.ForeignKey(
    #     "ObservationDefinitionCanonical",
    #     on_delete=models.DO_NOTHING,
    #     related_name="activity_definition_observation_requirement",
    #     null=True,
    # )

    # TODO: observation_result_requirement = models.ForeignKey(
    #     "ObservationDefinitionCanonical",
    #     on_delete=models.DO_NOTHING,
    #     related_name="activity_definition_observation_result_requirement",
    #     null=True,
    # )

    # TODO: transform = models.ForeignKey(
    #     "StructureMapCanonical",
    #     on_delete=models.DO_NOTHING,
    #     related_name="activity_definition_transform",
    #     null=True,
    # )
    dynamic_value = models.ManyToManyField(
        ActivityDefinitionDynamicValue,
        related_name="activity_definition_note",
        blank=True,
    )


class ActivityDefinitionReference(BaseReference):
    """ActivityDefinition reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_reference_identifier",
    )
    activity_definition = models.ForeignKey(
        ActivityDefinition,
        on_delete=models.DO_NOTHING,
        related_name="activity_definition_reference",
        null=True,
    )


class ActivityDefinitionPlanDefinitionReference(BaseReference):
    """activity plan definition reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_plan_definition_reference_identifier",
    )
    activity_definition = models.ForeignKey(
        ActivityDefinition,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_plan_definition_reference_activity_definition",
    )
    plan_definition = models.ForeignKey(
        "plandefinitions.PlanDefinition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_plan_definition_reference_plan_definition",
    )


class ActivityDefinitionPlanDefinitionCodeableReference(TimeStampedModel):
    """activity definition plan definition codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_plan_definition_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        ActivityDefinitionPlanDefinitionReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="activity_definition_plan_definition_codeable_reference_reference",
    )
