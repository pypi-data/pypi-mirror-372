"""AppointmentResponses models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)

from . import choices


class AppointmentResponseActorReference(BaseReference):
    """Appointment response actor reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="appointment_response_actor_reference_identifier",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="appointment_response_actor_reference_group",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="appointment_response_actor_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="appointment_response_actor_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="appointment_response_actor_reference_practitioner_role",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="appointment_response_actor_reference_related_person",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="appointment_response_actor_reference_device",
        null=True,
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthCareService",
        on_delete=models.CASCADE,
        related_name="appointment_response_actor_reference_healthcare_service",
        null=True,
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.CASCADE,
        related_name="appointment_response_actor_reference_location",
        null=True,
    )


class AppointmentResponse(TimeStampedModel):
    """Appointment response model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="appointment_response_identifier",
        blank=True,
    )
    appointment = models.ForeignKey(
        "appointments.AppointmentReference",
        on_delete=models.CASCADE,
        related_name="appointment_response_appointment",
        null=True,
    )
    proposed_new_time = models.BooleanField(null=True)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    participant_type = models.ManyToManyField(
        CodeableConcept,
        related_name="appointment_response_participant_type",
        blank=True,
    )
    actor = models.ForeignKey(
        AppointmentResponseActorReference,
        on_delete=models.CASCADE,
        related_name="appointment_response_actor",
        null=True,
    )
    participant_status = models.CharField(
        max_length=255,
        null=True,
        choices=choices.AppointmentResponseParticipantStatusChoices.choices,
    )
    comment = models.TextField(null=True)
    recurring = models.BooleanField(null=True)
    occurrence_date = models.DateTimeField(null=True)
    recurrence_id = models.IntegerField(null=True)
