"""transport models."""

from django.db import models

from dfhir.base.models import BaseReference, Identifier, TimeStampedModel
from dfhir.transports.choices import TransportStatusChoices


class TransportReference(BaseReference):
    """transport reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_reference_identifier",
    )
    transport = models.ForeignKey(
        "Transport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_reference_transport",
    )


class TransportBasedOnReference(BaseReference):
    """TransportBasedOn model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_based_on_identifier",
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_based_on_task",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_based_on_service_request",
    )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_based_on_device_request",
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_based_on_medication_request",
    )
    # TODO: requested_orchestration = models.ForeignKey(
    #     "requestedorchestrations.RequestedOrchestration",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="transport_based_on_requested_orchestration",
    # )
    supply_request = models.ForeignKey(
        "supplyrequests.SupplyRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_based_on_supply_request",
    )
    vision_prescription = models.ForeignKey(
        "visionprescriptions.VisionPrescription",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_based_on_vision_prescription",
    )


class TransportRequesterReference(BaseReference):
    """TransportRequester model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_requester_identifier",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_requester_device",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_requester_organization",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_requester_patient",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_requester_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_requester_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_requester_related_person",
    )


class TransportOwnerReference(BaseReference):
    """TransportOwnerReference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_owner_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_owner_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_owner_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_owner_reference_organization",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_owner_reference_care_team",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_owner_reference_healthcare_service",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_owner_reference_patient",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_owner_reference_device",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_owner_reference_related_person",
    )


class TransportRestrictionRecipientReference(BaseReference):
    """transport restriction recipient model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_restriction_recipient_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_restriction_recipient_patient",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_restriction_recipient_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_restriction_recipient_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_restriction_recipient_related_person",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_restriction_recipient_group",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_restriction_recipient_organization",
    )


class TransportRestriction(TimeStampedModel):
    """transport restriction model."""

    repetitions = models.PositiveIntegerField(null=True)
    period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_restriction_period",
    )
    recipient = models.ManyToManyField(
        TransportRestrictionRecipientReference,
        blank=True,
        related_name="transport_restriction_recipient",
    )


class TransportInput(TimeStampedModel):
    """transport input model."""

    type = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_input_type",
    )
    value = models.CharField(max_length=255, null=True)


class TransportOutput(TimeStampedModel):
    """transport output model."""

    type = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_output_type",
    )
    value = models.CharField(max_length=255, null=True)


class Transport(TimeStampedModel):
    """transport model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="transport_identifier", blank=True
    )
    # TODO: instantiates = models.ForeignKey(
    #     "ActivityDefinitionCanonical",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="transport_instantiates",
    # )
    based_on = models.ManyToManyField(
        TransportBasedOnReference,
        blank=True,
        related_name="transport_based_on",
    )
    group_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_group_identifier",
    )
    part_of = models.ManyToManyField(
        TransportReference,
        blank=True,
        related_name="transport_part_of",
    )
    status = models.CharField(
        max_length=255, null=True, choices=TransportStatusChoices.choices
    )
    status_reason = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_status_reason",
    )
    code = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_code",
    )
    description = models.TextField(null=True)
    focus = models.ForeignKey(
        "base.Reference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_focus",
    )
    for_value = models.ForeignKey(
        "base.Reference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_for_value",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_encounter",
    )
    completion_time = models.DateTimeField(null=True)
    authored_on = models.DateTimeField(null=True)
    last_modified = models.DateTimeField(null=True)
    requester = models.ForeignKey(
        TransportRequesterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_requester",
    )
    performer_type = models.ManyToManyField(
        "base.CodeableConcept", related_name="transport_performer_type", blank=True
    )
    owner = models.ForeignKey(
        TransportOwnerReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_owner",
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_location",
    )
    insurance = models.ManyToManyField(
        "coverages.CoverageClaimResponseReference",
        blank=True,
        related_name="transport_insurance",
    )
    note = models.ManyToManyField(
        "base.Annotation", related_name="transport_note", blank=True
    )
    relevant_history = models.ManyToManyField(
        "provenances.ProvenanceReference",
        related_name="transport_relevant_history",
        blank=True,
    )
    restriction = models.ForeignKey(
        TransportRestriction,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_restriction",
    )
    input = models.ManyToManyField(
        TransportInput, related_name="transport_input", blank=True
    )
    output = models.ManyToManyField(
        TransportOutput, related_name="transport_output", blank=True
    )
    requested_location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_requested_location",
    )
    current_location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_current_location",
    )
    reason = models.ForeignKey(
        "base.CodeableReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_reason",
    )
    history = models.ForeignKey(
        TransportReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="transport_history",
    )
