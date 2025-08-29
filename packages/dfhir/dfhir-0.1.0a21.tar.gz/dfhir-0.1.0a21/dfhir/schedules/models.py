"""Schedule model."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Period,
    TimeStampedModel,
)
from dfhir.healthcareservices.models import HealthCareServiceCodeableReference
from dfhir.practitioners.models import Practitioner


class SchedulesActorReference(BaseReference):
    """Actor model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="schedules_actor_identifier", blank=True
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="schedules_actor_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.DO_NOTHING,
        related_name="schedules_actor_practitioner",
        null=True,
    )
    healthcareservice = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        related_name="schedules_actor_healthcareservice",
        null=True,
    )


class Schedule(TimeStampedModel):
    """Schedule model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="schedule_identifier", blank=True
    )
    active = models.BooleanField(default=True)
    name = models.CharField(max_length=255, null=True)
    service_category = models.ManyToManyField(
        CodeableConcept, related_name="schedule_category"
    )
    specialty = models.ManyToManyField(
        CodeableConcept, related_name="schedule_specialty"
    )
    service_type = models.ManyToManyField(
        HealthCareServiceCodeableReference, related_name="schedule_servicetype"
    )
    slots_duration = models.IntegerField(default=30)
    planning_horizon = models.ForeignKey(Period, on_delete=models.DO_NOTHING, null=True)
    comment = models.TextField(null=True)
    actor = models.ManyToManyField(
        SchedulesActorReference, related_name="schedule_actor"
    )


class ScheduleReference(BaseReference):
    """ScheduleReference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="schedule_reference_identifier",
        null=True,
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.DO_NOTHING,
        related_name="schedule_reference_schedule",
        null=True,
    )
