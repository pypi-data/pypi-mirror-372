"""Encounter models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    OrganizationReference,
    Period,
    TimeStampedModel,
    VirtualServiceDetails,
)
from dfhir.base.models import (
    Quantity as Duration,
)
from dfhir.healthcareservices.models import (
    HealthCareServiceCodeableReference,
)

from .choices import EncounterLocationStatusChoices, EncounterStatus


class EncounterCondition(TimeStampedModel):
    """EncounterCondition model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class SpecialCourtesy(TimeStampedModel):
    """SpecialCourtesy model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class DietPreference(TimeStampedModel):
    """DietPreference model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class SpecialArrangement(TimeStampedModel):
    """SpecialArrangement model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class EncounterReference(BaseReference):
    """Encounter reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="encounter_reference_identifier",
        null=True,
    )
    encounter = models.ForeignKey(
        "Encounter",
        on_delete=models.CASCADE,
        related_name="encounter_reference_encounter",
        null=True,
    )


class EncounterReasonValueReference(BaseReference):
    """Reference to the condition, diagnostic report, observation, immunization recommendation, procedure."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_reason_value_reference_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_reason_value_reference_condition",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_reason_value_reference_diagnostic_report",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_reason_value_reference_observation",
    )
    immunization_recommendation = models.ForeignKey(
        "immunizationrecommendations.ImmunizationRecommendation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_reason_value_reference_immunization_recommendation",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_reason_value_reference_procedure",
    )


class EncounterReasonValueCodeableReference(TimeStampedModel):
    """EncounterReasonCodeableReference model."""

    reference = models.ForeignKey(
        EncounterReasonValueReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_reason_codeable_reference_reference",
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_reason_codeable_reference_concept",
    )


class EncounterReason(TimeStampedModel):
    """EncounterReason model."""

    use = models.ManyToManyField(
        CodeableConcept, related_name="encounter_reason_use", blank=True
    )
    value = models.ManyToManyField(
        EncounterReasonValueCodeableReference,
        related_name="encounter_reason_value",
        blank=True,
    )


class EncounterDiagnosis(TimeStampedModel):
    """EncounterDiagnosis model."""

    use = models.ManyToManyField(
        CodeableConcept, related_name="encounter_diagnosis_use", blank=True
    )
    condition = models.ManyToManyField(
        "conditions.ConditionCodeableReference",
        related_name="encounter_diagnosis_condition",
        blank=True,
    )


class EncounterBasedOnReference(BaseReference):
    """Reference to the care plan, device request, medication request, service request, request orchestration, nutrition order, visual prescription, and immunization recommendation."""

    # TODO: Implement the commentetd models
    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_based_on_reference_identifier",
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_based_on_reference_care_plan",
    )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_based_on_reference_device_request",
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_based_on_reference_medication_request",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_based_on_reference_service_request",
    )
    # request_orchestration = models.ForeignKey(
    #     "requestorchestrations.RequestOrchestration",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="encounter_based_on_reference_request_orchestration",
    # )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_based_on_reference_nutrition_order",
    )
    # visual_prescription = models.ForeignKey(
    #     "visualprescriptions.VisualPrescription",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="encounter_based_on_reference_visual_prescription",
    # )


class EncounterAdmission(TimeStampedModel):
    """EncounterAdmission model."""

    pre_admission_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_admission_pre_admission_identifier",
    )

    origin = models.ForeignKey(
        "locations.LocationOrganizationReference",
        related_name="admission_origin",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    admit_source = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_admission_admit_source",
    )
    re_admission = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_admission_re_admission",
    )
    destination = models.ForeignKey(
        "locations.LocationOrganizationReference",
        related_name="admission_destination",
        on_delete=models.CASCADE,
        null=True,
    )
    discharge_disposition = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_admission_discharge_disposition",
    )


class EncounterLocation(TimeStampedModel):
    """EncounterLocation model."""

    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        related_name="encounter_location_location",
        null=True,
    )
    status = models.CharField(
        max_length=255, choices=EncounterLocationStatusChoices.choices, null=True
    )
    form = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="encounter_location_form",
        null=True,
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="encounter_location_period",
        null=True,
    )


class EncounterParticipantActorReference(BaseReference):
    """EncounterParticipantActor model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="encounter_participant_actor_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="encounter_participant_actor_patient",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        related_name="encounter_participant_actor_group",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="encounter_participant_actor_related_person",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="encounter_participant_actor_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="encounter_participant_actor_practitioner_role",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        related_name="encounter_participant_actor_device",
        null=True,
    )
    healthcareservice = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        related_name="encounter_participant_actor_healthcareservice",
        null=True,
    )


class EncounterParticipant(TimeStampedModel):
    """Participants involved in the encounter."""

    actor = models.ForeignKey(
        EncounterParticipantActorReference,
        on_delete=models.CASCADE,
        null=True,
        related_name="participant_actor",
    )
    type = models.ManyToManyField(
        CodeableConcept, related_name="encounter_participant_type", blank=True
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_participant_period",
    )


class Encounter(TimeStampedModel):
    """Encounter model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="encounter_identifier", blank=True
    )
    status = models.CharField(
        max_length=255, choices=EncounterStatus.choices, null=True
    )
    klass = models.ManyToManyField(
        CodeableConcept, related_name="encounter_class", blank=True
    )
    priority = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_priority",
    )
    type = models.ManyToManyField(
        CodeableConcept, related_name="encounter_type", blank=True
    )
    service_type = models.ManyToManyField(
        HealthCareServiceCodeableReference, related_name="encounter_service_type"
    )
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        related_name="encounter_patient",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    subject_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_subject_status",
    )
    episode_of_care = models.ManyToManyField(
        "episodeofcares.EpisodeOfCare",
        related_name="encounter_episode_of_care",
        blank=True,
    )
    based_on = models.ManyToManyField(
        EncounterBasedOnReference, related_name="encounter_based_on", blank=True
    )
    care_team = models.ManyToManyField(
        "careteams.CareTeamReference", related_name="encounter_care_team", blank=True
    )
    part_of = models.ManyToManyField(
        EncounterReference, related_name="encounter_part_of", blank=True
    )
    service_provider = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        related_name="encounter_service_provider",
        null=True,
    )
    participant = models.ManyToManyField(
        EncounterParticipant, related_name="encounter_participant", blank=True
    )
    appointment = models.ManyToManyField(
        "appointments.AppointmentReference",
        related_name="encounter_appointment",
        blank=True,
    )
    virtual_service = models.ManyToManyField(
        VirtualServiceDetails, related_name="encounter_virtual_service", blank=True
    )
    actual_period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_actual_period",
    )
    planned_start_date = models.DateTimeField(null=True)
    planned_end_date = models.DateTimeField(null=True)
    # Quantity has the same fields as Duration and can be used interchangeably in this context
    length = models.ForeignKey(
        Duration,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_length",
    )
    reason = models.ManyToManyField(
        EncounterReason, related_name="encounter_reason", blank=True
    )
    diagnosis = models.ManyToManyField(
        EncounterDiagnosis, related_name="encounter_diagnosis", blank=True
    )
    account = models.ManyToManyField(
        "accounts.AccountReference", related_name="encounter_account", blank=True
    )
    diet_preference = models.ManyToManyField(
        CodeableConcept, related_name="encounter_diet_preference", blank=True
    )
    special_arrangement = models.ManyToManyField(
        CodeableConcept, related_name="encounter_special_arrangement", blank=True
    )
    special_courtesy = models.ManyToManyField(
        CodeableConcept, related_name="encounter_special_courtesy", blank=True
    )
    admission = models.ForeignKey(
        EncounterAdmission,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="encounter_admission",
    )
    location = models.ManyToManyField(
        EncounterLocation, related_name="encounter_location", blank=True
    )


class EncounterEpisodeOfCareReference(BaseReference):
    """EncounterEpisodeOfCareReference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="encounter_episode_of_care_reference_identifier",
        null=True,
    )
    episode_of_care = models.ForeignKey(
        "episodeofcares.EpisodeOfCare",
        on_delete=models.DO_NOTHING,
        related_name="encounter_episode_of_care_reference_episode_of_care",
        null=True,
    )
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.DO_NOTHING,
        related_name="encounter_episode_of_care_reference_encounter",
        null=True,
    )
