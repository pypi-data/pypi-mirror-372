"""document reference models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    CodeableReference,
    Coding,
    Identifier,
    Period,
    Reference,
    TimeStampedModel,
)
from dfhir.documentreferences.choices import (
    DocumentReferenceDocStatusChoices,
    DocumentReferenceStatusChoices,
)

# Create your models here.


class DocumentReferenceBasedOnReference(BaseReference):
    """document reference based on reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_references_identifier",
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_appointment",
    )
    appointment_response = models.ForeignKey(
        "appointmentresponses.AppointmentResponse",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="document_reference_based_on_reference_appointment_response",
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_care_plan",
    )
    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_claim",
    )
    # TODO: communication_request = models.ForeignKey(
    #     "communications.CommunicationRequest",
    #     on_delete=models.DO_NOTHING,
    #     null=True)
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_contract",
    )
    coverage_eligibility_request = models.ForeignKey(
        "coverageeligibilityrequests.CoverageEligibilityRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_coverage_eligibility_request",
    )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_device_request",
    )
    enrollment_request = models.ForeignKey(
        "enrollmentrequests.EnrollmentRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_enrollment_request",
    )
    immunization_recommendation = models.ForeignKey(
        "immunizationrecommendations.ImmunizationRecommendation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_immunization_recommendation",
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_medication_request",
    )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_nutrition_order",
    )
    # TODO: request_orchestration = models.ForeignKey(
    #     "requestorchestrations.RequestOrchestration",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="document_reference_based_on_reference_request_orchestration",
    # )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_service_request",
    )
    supply_request = models.ForeignKey(
        "supplyrequests.SupplyRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_supply_request",
    )
    vision_prescription = models.ForeignKey(
        "visionprescriptions.VisionPrescription",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_based_on_reference_vision_prescription",
    )


class DocumentReferenceAuthorReference(BaseReference):
    """document reference author reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_author_references_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_author_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_author_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_author_reference_organization",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_author_reference_device",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_author_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_author_reference_related_person",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_author_reference_care_team",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_author_reference_group",
    )


class DocumentReferenceAttesterPartyReference(BaseReference):
    """document reference attester party reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_attester_party_references_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_attester_party_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_attester_party_reference_related_person",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_attester_party_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_attester_party_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_attester_party_reference_organization",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_attester_party_reference_group",
    )


class DocumentReferenceAttester(TimeStampedModel):
    """document reference attester model."""

    mode = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_attesters_mode",
    )
    time = models.DateTimeField(null=True)
    party = models.ForeignKey(
        DocumentReferenceAttesterPartyReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_attesters_party",
    )


class DocumentReferenceRelatesTo(TimeStampedModel):
    """document reference relates to."""

    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_relates_tos_code",
    )
    target = models.ForeignKey(
        "DocumentReferenceReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_relates_tos_target",
    )


class DocumentReferenceContentProfile(TimeStampedModel):
    """document reference content profile model."""

    value_coding = models.ForeignKey(
        Coding,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_content_profiles_value_coding",
    )
    value_uri = models.URLField(null=True)
    # TODO: value_canonical = models.ForeignKey("Canonical", on_delete=models.DO_NOTHING, null=True)


class DocumentReferenceContent(TimeStampedModel):
    """document reference content model."""

    attachment = models.ForeignKey(
        "base.Attachment",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_contents_attachment",
    )
    profile = models.ManyToManyField(
        DocumentReferenceContentProfile,
        related_name="document_reference_contents_profile",
        blank=True,
    )


class DocumentReferenceContextReference(TimeStampedModel):
    """document reference context reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_context_references_identifier",
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="document_reference_context_reference_appointment",
    )
    encounter = models.ForeignKey(
        "encounters.Encounter",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_context_reference_encounter",
    )
    episode_of_care = models.ForeignKey(
        "episodeofcares.EpisodeOfCare",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_context_reference_episode_of_care",
    )


class DocumentReference(TimeStampedModel):
    """document reference model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="document_reference_identifier"
    )
    version = models.CharField(max_length=255, null=True)
    based_on = models.ManyToManyField(
        DocumentReferenceBasedOnReference,
        blank=True,
        related_name="document_reference_based_on",
    )
    status = models.CharField(
        max_length=255, null=True, choices=DocumentReferenceStatusChoices.choices
    )
    doc_status = models.CharField(
        max_length=255, null=True, choices=DocumentReferenceDocStatusChoices.choices
    )
    modality = models.ManyToManyField(
        CodeableConcept, related_name="document_reference_modalities", blank=True
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_type",
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="document_reference_categories", blank=True
    )
    subject = models.ForeignKey(
        Reference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_subject",
    )
    context = models.ManyToManyField(
        DocumentReferenceContextReference,
        related_name="document_reference_contexts",
        blank=True,
    )
    event = models.ManyToManyField(
        CodeableReference, related_name="document_reference_events", blank=True
    )
    related = models.ManyToManyField(
        Reference, related_name="document_reference_related", blank=True
    )
    body_site = models.ManyToManyField(
        "bodystructures.BodyStructureCodeableReference",
        related_name="document_reference_body_sites",
        blank=True,
    )
    facility_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_facility_type",
    )
    practice_setting = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_practice_setting",
    )
    period = models.ForeignKey(
        Period,
        related_name="document_reference_source_patient_infos",
        null=True,
        on_delete=models.DO_NOTHING,
    )
    date = models.DateTimeField(null=True)
    author = models.ManyToManyField(
        DocumentReferenceAuthorReference,
        related_name="document_reference_authors",
        blank=True,
    )
    attester = models.ManyToManyField(
        DocumentReferenceAttester,
        related_name="document_reference_attesters",
        blank=True,
    )
    custodian = models.ForeignKey(
        "base.OrganizationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_custodian",
    )
    relates_to = models.ManyToManyField(
        DocumentReferenceRelatesTo,
        related_name="document_reference_relates_tos",
        blank=True,
    )
    description = models.TextField(null=True)
    security_label = models.ManyToManyField(
        CodeableConcept, related_name="document_reference_security_labels", blank=True
    )
    content = models.ManyToManyField(
        DocumentReferenceContent, related_name="document_reference_contents", blank=True
    )


class DocumentReferenceReference(BaseReference):
    """document reference reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_references_identifier",
    )
    document_reference = models.ForeignKey(
        DocumentReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_references_document_reference",
    )


class DocumentReferenceCodeableReference(TimeStampedModel):
    """document reference codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_codeable_references_concept",
    )
    reference = models.ForeignKey(
        Reference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_codeable_references_reference",
    )
