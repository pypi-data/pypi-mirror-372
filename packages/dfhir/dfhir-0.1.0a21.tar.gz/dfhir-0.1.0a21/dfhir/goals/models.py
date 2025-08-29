"""Goals models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Duration,
    Identifier,
    Quantity,
    Range,
    Ratio,
    TimeStampedModel,
)

from . import choices


class GoalSubjectReference(BaseReference):
    """Goal Subject Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="goal_subject_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="goal_subject_reference_patient",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        related_name="goal_subject_reference_group",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="goal_subject_reference_organization",
        null=True,
    )


class GoalAcceptanceParticipantReference(BaseReference):
    """Goal Acceptance Participant Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="goal_acceptance_participant_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="goal_acceptance_participant_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="goal_acceptance_participant_reference_practitioner",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="goal_acceptance_participant_reference_related_person",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="goal_acceptance_participant_reference_practitioner_role",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        related_name="goal_acceptance_participant_reference_care_team",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="goal_acceptance_participant_reference_organization",
        null=True,
    )


class GoalAcceptance(TimeStampedModel):
    """Goal Acceptance model."""

    participant = models.ForeignKey(
        GoalAcceptanceParticipantReference,
        on_delete=models.DO_NOTHING,
        related_name="goal_acceptance_participant",
        null=True,
    )
    status = models.CharField(
        max_length=255, choices=choices.GoalAcceptanceStatusChoices.choices
    )
    priority = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="goal_acceptance_priority",
        null=True,
    )


class GoalTarget(TimeStampedModel):
    """Goal Target model."""

    measure = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="goal_target_measure",
        null=True,
    )
    detail_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        related_name="goal_target_detail_quantity",
        null=True,
    )
    detail_range = models.ForeignKey(
        Range,
        on_delete=models.DO_NOTHING,
        related_name="goal_target_detail_range",
        null=True,
    )
    detail_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="goal_target_detail_codeable_concept",
        null=True,
    )
    detail_string = models.CharField(max_length=255, null=True)
    detail_boolean = models.BooleanField(default=False)
    detail_integer = models.IntegerField(null=True)
    detail_ratio = models.ForeignKey(
        Ratio,
        on_delete=models.DO_NOTHING,
        related_name="goal_target_detail_ratio",
        null=True,
    )
    due_date = models.DateField(null=True)
    due_duration = models.ForeignKey(
        Duration,
        on_delete=models.DO_NOTHING,
        related_name="goal_target_due_duration",
        null=True,
    )


class GoalSourceReference(BaseReference):
    """Goal source reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="goal_source_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="goal_source_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="goal_source_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="goal_source_reference_practitioner_role",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="goal_source_reference_related_person",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.CASCADE,
        related_name="goal_source_reference_care_team",
        null=True,
    )


class GoalAddressesReference(BaseReference):
    """Goal addresses reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="goal_addresses_reference_identifier",
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.CASCADE,
        related_name="goal_addresses_reference_condition",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.CASCADE,
        related_name="goal_addresses_reference_observation",
        null=True,
    )

    medication_statement = models.ForeignKey(
        "medicationstatements.MedicationStatement",
        on_delete=models.CASCADE,
        related_name="goal_addresses_reference_medication_statement",
        null=True,
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.CASCADE,
        related_name="goal_addresses_reference_medication_request",
        null=True,
    )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.CASCADE,
        related_name="goal_addresses_reference_nutrition_order",
        null=True,
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="goal_addresses_reference_service_request",
        null=True,
    )
    risk_assessment = models.ForeignKey(
        "riskassessments.RiskAssessment",
        on_delete=models.CASCADE,
        related_name="goal_addresses_reference_risk_assessment",
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.CASCADE,
        related_name="goal_addresses_reference_procedure",
        null=True,
    )
    nutrition_intake = models.ForeignKey(
        "nutritionintakes.NutritionIntake",
        on_delete=models.CASCADE,
        related_name="goal_addresses_reference_nutrition_intake",
        null=True,
    )


class Goal(TimeStampedModel):
    """Goal model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="goal_identifier",
        blank=True,
    )
    lifecycle_status = models.CharField(
        max_length=255, choices=choices.GoalLifecycleStatusChoices.choices
    )
    achievement_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="goal_achievement_status",
        null=True,
    )
    category = models.ManyToManyField(
        CodeableConcept,
        related_name="goal_category",
        blank=True,
    )
    continuous = models.BooleanField(default=False)
    priority = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="goal_priority",
        null=True,
    )
    description = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="goal_description",
        null=True,
    )
    subject = models.ForeignKey(
        GoalSubjectReference,
        on_delete=models.DO_NOTHING,
        related_name="goal_subject",
        null=True,
    )
    start_date = models.DateField(null=True)
    start_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="goal_start_code",
        null=True,
    )
    acceptance = models.ManyToManyField(
        GoalAcceptance,
        related_name="goal_acceptance",
        blank=True,
    )
    target = models.ManyToManyField(
        GoalTarget,
        related_name="goal_target",
        blank=True,
    )
    status_date = models.DateField(null=True)
    status_reason = models.ManyToManyField(
        CodeableConcept,
        related_name="goal_status_code",
        blank=True,
    )
    source = models.ForeignKey(
        GoalSourceReference,
        on_delete=models.DO_NOTHING,
        related_name="goal_source",
        null=True,
    )
    addresses = models.ManyToManyField(
        GoalAddressesReference,
        related_name="goal_addresses",
        blank=True,
    )
    note = models.ManyToManyField(
        Annotation,
        related_name="goal_note",
        blank=True,
    )
