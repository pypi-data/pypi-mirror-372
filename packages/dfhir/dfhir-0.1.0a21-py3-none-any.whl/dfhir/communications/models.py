"""communications app models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    Attachment,
    BaseReference,
    CodeableConcept,
    CodeableReference,
    Coding,
    Identifier,
    Reference,
    TimeStampedModel,
)
from dfhir.encounters.models import EncounterReference
from dfhir.patients.models import PatientGroupReference


class CommunicationRequestReference(BaseReference):
    """communication request reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_request_reference_identifier",
    )
    # TODO: communication_request = models.ForeignKey(
    #     "communications.CommunicationRequest",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="communication_request_reference_communication_request",
    # )


class CommunicationRecipientReference(BaseReference):
    """communication recipient reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_recipient_reference_identifier",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_recipient_reference_care_team",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_recipient_reference_device",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_recipient_reference_group",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_recipient_reference_healthcare_service",
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_recipient_reference_location",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_recipient_reference_organization",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_recipient_reference_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_recipient_reference_related_person",
    )
    endpoint = models.ForeignKey(
        "endpoints.Endpoint",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_recipient_reference_endpoint",
    )


class CommunicationSenderReference(BaseReference):
    """communication sender reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender_reference_identifier",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender_reference_device",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender_reference_organization",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender_reference_patient",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender_reference_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender_reference_related_person",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender_reference_healthcare_service",
    )
    endpoint = models.ForeignKey(
        "endpoints.Endpoint",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender_reference_endpoint",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender_reference_care_team",
    )


class CommunicationPayload(TimeStampedModel):
    """communication payload model."""

    content_attachment = models.ForeignKey(
        Attachment,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_payload_content_attachment",
    )
    content_reference = models.ForeignKey(
        Reference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_payload_content_reference",
    )
    content_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_payload_content_codeable_concept",
    )


class CommunicationBsedOnReference(BaseReference):
    """communication based on reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_based_on_reference_identifier",
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_based_on_reference_care_plan",
    )
    # TODO: communication_request = models.ForeignKey(
    #     "communications.CommunicationRequest",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="communication_based_on_reference_communication_request",
    # )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_based_on_reference_device_request",
    )
    immunization_recommendation = models.ForeignKey(
        "immunizationrecommendations.ImmunizationRecommendation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_based_on_reference_immunization_recommendation",
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_based_on_reference_medication_request",
    )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_based_on_reference_nutrition_order",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_based_on_reference_service_request",
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_based_on_reference_task",
    )
    vision_prescription = models.ForeignKey(
        "visionprescriptions.VisionPrescription",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_based_on_reference_vision_prescription",
    )


class Communication(TimeStampedModel):
    """communication model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="communication_identifier", blank=True
    )
    based_on = models.ManyToManyField(
        CommunicationBsedOnReference,
        related_name="communication_based_on",
        blank=True,
    )
    part_of = models.ManyToManyField(
        Reference, related_name="communication_part_of", blank=True
    )
    in_response_to = models.ManyToManyField(
        "communications.CommunicationReference",
        related_name="communication_in_response_to",
        blank=True,
    )
    status = models.ForeignKey(
        Coding,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_status",
    )
    status_reason = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_status_reason",
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="communication_category", blank=True
    )
    priority = models.ForeignKey(
        Coding,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_priority",
    )
    medium = models.ManyToManyField(
        CodeableConcept, related_name="communication_medium", blank=True
    )
    subject = models.ForeignKey(
        PatientGroupReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_subject",
    )
    topic = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_topic",
    )
    about = models.ManyToManyField(
        Reference, related_name="communication_about", blank=True
    )
    encounter = models.ForeignKey(
        EncounterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_encounter",
    )
    sent = models.DateTimeField(null=True)
    received = models.DateTimeField(null=True)
    recipient = models.ManyToManyField(
        CommunicationRecipientReference,
        related_name="communication_recipient",
        blank=True,
    )
    sender = models.ForeignKey(
        CommunicationSenderReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_sender",
    )
    reason = models.ManyToManyField(
        CodeableReference, related_name="communication_reason_code", blank=True
    )
    payload = models.ManyToManyField(
        CommunicationPayload, related_name="communication_payload", blank=True
    )
    note = models.ManyToManyField(
        Annotation, related_name="communication_note", blank=True
    )


class CommunicationReference(BaseReference):
    """communication reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_reference_identifier",
    )
    communication = models.ForeignKey(
        Communication,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="communication_reference_communication",
    )
