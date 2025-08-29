"""Slots models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)
from dfhir.healthcareservices.models import HealthCareServiceCodeableReference
from dfhir.practitioners.models import Practitioner
from dfhir.schedules.models import Schedule

from .choices import AppointmentType, SlotStatus


class SlotReference(BaseReference):
    """Slot reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="slot_reference_identifier",
        null=True,
    )
    slot = models.ForeignKey(
        "Slot",
        on_delete=models.CASCADE,
        related_name="slot_reference_slot",
        null=True,
    )


class Slot(TimeStampedModel):
    """Slot model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="slot_identifier", blank=True
    )
    practitioner = models.ForeignKey(
        Practitioner, on_delete=models.DO_NOTHING, related_name="slot_practitioner"
    )
    service_category = models.ManyToManyField(
        CodeableConcept, related_name="slot_service_category", blank=True
    )
    service_type = models.ManyToManyField(
        HealthCareServiceCodeableReference, related_name="slot_service_type", blank=True
    )
    specialty = models.ManyToManyField(
        CodeableConcept, related_name="slot_specialty", blank=True
    )
    appointment_type = ArrayField(
        models.CharField(max_length=255, choices=AppointmentType.choices), null=True
    )
    schedule = models.ForeignKey(
        Schedule, on_delete=models.DO_NOTHING, null=True, related_name="slot_schedule"
    )
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    overbooked = models.BooleanField(default=False)
    comment = models.TextField(null=True)
    status = models.CharField(
        max_length=255, choices=SlotStatus.choices, default=SlotStatus.FREE
    )
