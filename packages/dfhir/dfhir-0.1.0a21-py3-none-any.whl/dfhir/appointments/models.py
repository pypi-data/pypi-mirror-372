"""Appointments models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Coding,
    Identifier,
    Period,
    Reference,
    TimeStampedModel,
    VirtualServiceDetails,
)
from dfhir.healthcareservices.models import HealthCareServiceCodeableReference
from dfhir.locations.models import Location
from dfhir.practitioners.models import Practitioner

from .choices import (
    AppointmentStatus,
    ParticipationStatusChoices,
)


class AppointmentReasonReference(BaseReference):
    """Reference to the condition, procedure, observation, or immunization recommendation."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_reason_identifier",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_reason_observation",
    )


class AppointmentReasonCodeableReference(TimeStampedModel):
    """Reference to the condition, procedure, observation, or immunization recommendation."""

    reference = models.ForeignKey(
        AppointmentReasonReference,
        on_delete=models.DO_NOTHING,
        related_name="appointment_reason_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="appointment_reason_concept",
        null=True,
    )


class WeeklyTemplate(TimeStampedModel):
    """WeeklyTemplate model is used to store the weekly recurrence pattern."""

    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    week_interval = models.PositiveIntegerField(null=True)


class MonthlyTemplate(TimeStampedModel):
    """MonthlyTemplate model is used to store the monthly recurrence pattern."""

    day_of_month = models.PositiveIntegerField()
    day_of_week = models.ForeignKey(
        Coding,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="monthly_template_day_of_week",
    )
    nth_week_of_month = models.ForeignKey(
        Coding,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="monthly_template_nth_week_of_month",
    )
    month_interval = models.PositiveIntegerField()


class YearlyTemplate(TimeStampedModel):
    """YearlyTemplate model is used to store the yearly recurrence pattern."""

    year_interval = models.PositiveIntegerField()


class RecurrenceTemplate(TimeStampedModel):
    """Details of the recurrence pattern/template used to generate occurrences."""

    recurrence_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="recurrence_type",
    )
    last_occurrence_date = models.DateField(null=True, blank=True)
    occurrence_count = models.PositiveIntegerField(null=True, blank=True)
    occurrence_date = models.DateField(null=True, blank=True)
    excluding_recurrence_id = ArrayField(models.PositiveIntegerField(), null=True)
    time_zone = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="recurrence_time_zone",
    )
    weekly_template = models.ForeignKey(
        WeeklyTemplate, on_delete=models.DO_NOTHING, null=True
    )
    monthly_template = models.ForeignKey(
        MonthlyTemplate, on_delete=models.DO_NOTHING, null=True
    )
    yearly_template = models.ForeignKey(
        YearlyTemplate, on_delete=models.DO_NOTHING, null=True
    )
    excluding_date = ArrayField(models.DateField(), null=True)


class AppointmentEncounterReason(TimeStampedModel):
    """Reason this appointment is scheduled."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class AppointmentBasedOnReference(BaseReference):
    """Reference to the care plan, device request, medication request, service request, request orchestration, nutrition order, visual prescription, and immunization recommendation."""

    # TODO: Implement the commentetd models
    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_based_on_reference_identifier",
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_based_on_reference_care_plan",
    )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_based_on_reference_device_request",
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_based_on_reference_medication_request",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_based_on_reference_service_request",
    )
    # request_orchestration = models.ForeignKey(
    #     "requestorchestrations.RequestOrchestration",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="appointment_based_on_reference_request_orchestration",
    # )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_based_on_reference_nutrition_order",
    )
    # visual_prescription = models.ForeignKey(
    #     "visualprescriptions.VisualPrescription",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="appointment_based_on_reference_visual_prescription",
    # )


class DocumentReferenceBinaryCommunicationReference(BaseReference):
    """Reference to the patient instructions."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="document_reference_binary_communication_reference_identifier",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        related_name="document_reference_binary_communication_reference_document_reference",
        null=True,
    )
    # binary = models.ForeignKey(
    #     "binaries.Binary",
    #     on_delete=models.DO_NOTHING,
    #     related_name="document_reference_binary_communication_reference_binary",
    #     null=True,
    # )
    communication = models.ForeignKey(
        "communications.Communication",
        on_delete=models.DO_NOTHING,
        related_name="document_reference_binary_communication_reference_communication",
        null=True,
    )


class AppointmentParticipantActor(BaseReference):
    """Reference to the patient, group, practitioner, practitioner role, care team, related person, device, healthcare service, and location."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="appointment_participant_actor_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="appointment_participant_actor_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.DO_NOTHING,
        related_name="appointment_participant_actor_practitioner",
        null=True,
    )
    healthcareservice = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        related_name="appointment_participant_actor_healthcareservice",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        related_name="appointment_participant_actor_device",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        related_name="appointment_participant_actor_group",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        related_name="appointment_participant_actor_care_team",
        null=True,
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.DO_NOTHING,
        related_name="appointment_participant_actor_location",
        null=True,
    )


class AppointmentParticipant(TimeStampedModel):
    """Participants involved in the appointment."""

    actor = models.ForeignKey(
        AppointmentParticipantActor,
        on_delete=models.CASCADE,
        null=True,
        related_name="appointment_participant_actor",
    )
    type = models.ManyToManyField(
        CodeableConcept, related_name="appointment_participant_type", blank=True
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_participant_period",
    )
    required = models.BooleanField(default=False)
    status = models.CharField(
        max_length=255, choices=ParticipationStatusChoices.choices, null=True
    )


class AppointmentReference(BaseReference):
    """Appointment reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="appointment_reference_identifier",
        null=True,
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="appointment_reference_appointment",
        null=True,
    )


class Appointment(TimeStampedModel):
    """Appointment model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="appointment_identifier", blank=True
    )

    status = models.CharField(
        max_length=255, choices=AppointmentStatus.choices, null=True
    )
    cancellation_reason = models.ForeignKey(
        CodeableConcept, on_delete=models.DO_NOTHING, null=True
    )
    klass = models.ManyToManyField(
        CodeableConcept, related_name="appointment_class", blank=True
    )
    service_category = models.ManyToManyField(
        CodeableConcept, related_name="service_category", blank=True
    )
    service_type = models.ManyToManyField(
        HealthCareServiceCodeableReference,
        related_name="appointment_service_type",
        blank=True,
    )
    specialty = models.ManyToManyField(
        CodeableConcept, related_name="appointment_specialty", blank=True
    )
    appointment_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_type",
    )
    reason = models.ManyToManyField(
        AppointmentReasonCodeableReference,
        related_name="appointment_reason",
        blank=True,
    )
    priority = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_priority",
    )
    description = models.TextField(blank=True, null=True)
    replaces = models.ManyToManyField(
        AppointmentReference, related_name="appointment_replaces", blank=True
    )
    virtual_service = models.ManyToManyField(
        VirtualServiceDetails,
        related_name="appointment_virtual_service_details",
        blank=True,
    )
    supporting_information = models.ManyToManyField(
        Reference, related_name="appointment_supporting_information", blank=True
    )
    previous_appointment = models.ForeignKey(
        AppointmentReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_previous_appointment",
    )
    originating_appointment = models.ForeignKey(
        AppointmentReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="appointment_originating_appointment",
    )
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    minutes_duration = models.PositiveIntegerField(null=True)
    requested_period = models.ManyToManyField(
        Period, related_name="appointment_requested_period", blank=True
    )
    slot = models.ManyToManyField(
        "slots.SlotReference", related_name="appointment_slot", blank=True
    )
    # TODO: uncomment after implementing accounts model

    account = models.ManyToManyField(
        "accounts.AccountReference", related_name="appointment_account", blank=True
    )
    cancellation_date = models.DateTimeField(
        null=True, blank=True, help_text="Date of cancellation"
    )
    note = models.ManyToManyField(
        Annotation, related_name="appointment_note", blank=True
    )
    patient_instruction = models.ManyToManyField(
        DocumentReferenceBinaryCommunicationReference,
        related_name="appointment_patient_instruction",
        blank=True,
    )
    based_on = models.ManyToManyField(
        AppointmentBasedOnReference,
        related_name="appointment_based_on",
        blank=True,
    )
    recurrence_id = models.PositiveIntegerField(null=True, blank=True)
    occurrence_changed = models.BooleanField(default=False)
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.DO_NOTHING,
        related_name="appointment_subject",
        null=True,
    )
    participant = models.ManyToManyField(
        AppointmentParticipant, related_name="appointment_participant", blank=True
    )
