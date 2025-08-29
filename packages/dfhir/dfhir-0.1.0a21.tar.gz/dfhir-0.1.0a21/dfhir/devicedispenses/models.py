"""Devicedispenses models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    Reference,
    SimpleQuantity,
    TimeStampedModel,
)

from . import choices


class DeviceDispenseReceiverReference(BaseReference):
    """DeviceDispenseReceiverReference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="device_dispense_receiver_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="device_dispense_receiver_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="device_dispense_receiver_reference_practitioner",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="device_dispense_receiver_reference_related_person",
        null=True,
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.CASCADE,
        related_name="device_dispense_receiver_reference_location",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="device_dispense_receiver_reference_practitioner_role",
        null=True,
    )


class DeviceDispensePerformerActorReference(BaseReference):
    """DeviceDispensePerformerActorReference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="device_dispense_performer_actor_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="device_dispense_performer_actor_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="device_dispense_performer_actor_reference_practitioner",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="device_dispense_performer_actor_reference_organization",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="device_dispense_performer_actor_reference_practitioner_role",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="device_dispense_performer_actor_reference_device",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="device_dispense_performer_actor_reference_device_related_person",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.CASCADE,
        related_name="device_dispense_performer_actor_reference_device_care_team",
        null=True,
    )


class DeviceDispensePerformer(TimeStampedModel):
    """DeviceDispensePerformer model."""

    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="device_dispense_performer_function",
        null=True,
    )
    actor = models.ForeignKey(
        DeviceDispensePerformerActorReference,
        on_delete=models.CASCADE,
        related_name="device_dispense_performer_actor",
        null=True,
    )


class DeviceDispense(TimeStampedModel):
    """DeviceDispense model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="device_dispense_identifier",
        blank=True,
    )
    based_on = models.ManyToManyField(
        "careplans.CarePlanDeviceRequestReference",
        related_name="device_dispense_based_on",
        blank=True,
    )
    part_of = models.ManyToManyField(
        "procedures.ProcedureReference",
        related_name="device_dispense_part_of",
        blank=True,
    )
    status = models.CharField(
        max_length=255, choices=choices.DeviceDispenseStatus.choices, null=True
    )
    status_reason = models.ForeignKey(
        "detectedissues.DetectedIssueCodeableReference",
        on_delete=models.CASCADE,
        related_name="device_dispense_status_reason",
        null=True,
    )
    category = models.ManyToManyField(
        CodeableConcept,
        related_name="device_dispense_category",
        blank=True,
    )
    device = models.ForeignKey(
        "devicedefinitions.DeviceDeviceDefinitionCodeableReference",
        on_delete=models.CASCADE,
        related_name="device_dispense_device",
        null=True,
    )
    subject = models.ForeignKey(
        "patients.PatientPractitionerReference",
        on_delete=models.CASCADE,
        related_name="device_dispense_subject",
        null=True,
    )
    receiver = models.ForeignKey(
        DeviceDispenseReceiverReference,
        on_delete=models.CASCADE,
        related_name="device_dispense_receiver",
        null=True,
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.CASCADE,
        related_name="device_dispense_encounter",
        null=True,
    )
    supporting_information = models.ManyToManyField(
        Reference,
        related_name="device_dispense_supporting_information",
        blank=True,
    )
    performer = models.ManyToManyField(
        DeviceDispensePerformer,
        related_name="device_dispense_performer",
        blank=True,
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.CASCADE,
        related_name="device_dispense_location",
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="device_dispense_type",
        null=True,
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.CASCADE,
        related_name="device_dispense_quantity",
        null=True,
    )

    prepared_date = models.DateTimeField(null=True)
    when_handed_over = models.DateTimeField(null=True)
    destination = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.CASCADE,
        related_name="device_dispense_destination",
        null=True,
    )
    note = models.ManyToManyField(
        Annotation,
        related_name="device_dispense_note",
        blank=True,
    )

    usage_instruction = models.TextField(null=True)
    event_history = models.ManyToManyField(
        "provenances.ProvenanceReference",
        related_name="device_dispense_event_history",
        blank=True,
    )
