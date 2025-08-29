"""nutrition intakes models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Reference,
    TimeStampedModel,
)
from dfhir.nutritionintakes.choices import NutritionIntakeStatusChoices
from dfhir.substances.models import SubstanceCodeableReference


class NutritionIntakeBasedOnReference(BaseReference):
    """Nutrition intake based on reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_based_on_reference_identifier",
    )
    # TODO: nutrition_order = models.ForeignKey("NutritionOrder", on_delete=models.DO_NOTHING, null=True)
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_based_on_reference_care_plan",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_based_on_reference_service_request",
    )


class NutritionIntakePartOfReference(BaseReference):
    """Nutrition intake part of reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_part_of_reference_identifier",
    )
    nutrition_intake = models.ForeignKey(
        "NutritionIntake",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_part_of_reference_nutrition_intake",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_part_of_reference_procedure",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_part_of_reference_observation",
    )


class NutritionIntakeReportedReference(BaseReference):
    """Nutrition intake reported reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reported_reference_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reported_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reported_reference_related_person",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reported_reference_practitioner",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reported_reference_organization",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reported_reference_group",
    )


class NutritionIntakeNutritionItemTotalIntake(TimeStampedModel):
    """nutrition intake nutrition item total intake model."""

    nutrient = models.ForeignKey(
        SubstanceCodeableReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_nutrition_item_total_intake_nutrient",
    )
    amount = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_nutrition_item_total_intake_amount",
    )
    energy = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_nutrition_item_total_intake_energy",
    )


class NutritionIntakeNutritionItemConsumedItem(TimeStampedModel):
    """nutrition intake nutrition item consumed item model."""

    schedule = models.ForeignKey(
        "base.Timing",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_nutrition_item_consumed_item_schedule",
    )
    amount = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_nutrition_item_consumed_item_amount",
    )
    rate_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_nutrition_item_consumed_item_rate_quantity",
    )
    rate_ratio = models.ForeignKey(
        "base.Ratio",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_nutrition_item_consumed_item_rate_ratio",
    )
    total_intake = models.ManyToManyField(
        NutritionIntakeNutritionItemTotalIntake,
        blank=True,
        related_name="nutrition_intake_nutrition_item_consumed_item_total_intake",
    )


class NutritionIntakeNutritionItem(TimeStampedModel):
    """nutrition intake nutrition item model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_nutrition_item_type",
    )
    nutrition_product = models.ForeignKey(
        "nutritionproducts.NutritionProductCodeableReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_nutrition_item_nutrition_product",
    )
    consumed_item = models.ManyToManyField(
        NutritionIntakeNutritionItemConsumedItem,
        related_name="nutrition_intake_nutrition_item_consumed_item",
        blank=True,
    )
    not_consumed = models.BooleanField(default=False)
    not_consumed_reason = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_nutrition_item_not_consumed_reason",
    )


class NutritionIntakePerformerActorReference(BaseReference):
    """nutrition intake performer actor reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_actor_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_actor_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_actor_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_actor_reference_organization",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_actor_reference_care_team",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_actor_reference_patient",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_actor_reference_device",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_actor_reference_related_person",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_actor_reference_group",
    )


class NutritionIntakePerformer(TimeStampedModel):
    """nutrition intake performer reference model."""

    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_reference_function",
    )
    actor = models.ForeignKey(
        NutritionIntakePerformerActorReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_performer_reference_actor",
    )


class NutritionIntakeReasonReference(BaseReference):
    """nutrition intake reason reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reason_reference_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reason_reference_condition",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reason_reference_observation",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reason_reference_diagnostic_report",
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reason_reference_document_reference",
    )


class NutritionIntakeReasonCodeableReference(TimeStampedModel):
    """nutrition intake codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reason_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        NutritionIntakeReasonReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_codeable_reference_reference",
    )


class NutritionIntake(TimeStampedModel):
    """nutrition intake model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="nutrition_intake_identifier"
    )
    # TODO: instantiates_canonical = models.ManyToManyField(Definition)
    instantiates_uri = models.URLField(null=True)
    based_on = models.ManyToManyField(
        NutritionIntakeBasedOnReference,
        related_name="nutrition_intake_based_on",
        blank=True,
    )
    part_of = models.ManyToManyField(
        NutritionIntakePartOfReference,
        blank=True,
        related_name="nutrition_intake_part_of",
    )
    status = models.CharField(
        max_length=200, null=True, choices=NutritionIntakeStatusChoices.choices
    )
    status_reason = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="nutrition_intake_status_reason",
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_code",
    )
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_subject",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_encounter",
    )
    occurrence_date_time = models.DateTimeField(null=True)
    occurrence_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_occurrence_period",
    )
    recorded = models.DateTimeField(null=True)
    reported_boolean = models.BooleanField(null=True)
    reported_reference = models.ForeignKey(
        NutritionIntakeReportedReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reported_reference",
    )
    nutrition_item = models.ManyToManyField(
        NutritionIntakeNutritionItem,
        related_name="nutrition_intake_nutrition_item",
        blank=True,
    )
    performer = models.ManyToManyField(
        NutritionIntakePerformer,
        related_name="nutrition_intake_performer",
        blank=True,
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_location",
    )
    derived_from = models.ManyToManyField(
        Reference, blank=True, related_name="nutrition_intake_derived_from"
    )
    reason = models.ManyToManyField(
        NutritionIntakeReasonCodeableReference,
        blank=True,
        related_name="nutrition_intake_reason_code",
    )
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="nutrition_intake_note"
    )


class NutritionIntakeReference(BaseReference):
    """nutrition intake reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reference_identifier",
    )
    nutrition_intake = models.ForeignKey(
        "NutritionIntake",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_reference_nutrition_intake",
    )


class NutritionIntakeCodeableReference(TimeStampedModel):
    """nutrition intake codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        NutritionIntakeReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="nutrition_intake_codeable_reference_reference",
    )
