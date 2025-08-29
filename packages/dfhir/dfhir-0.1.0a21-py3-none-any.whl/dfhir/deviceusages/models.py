"""Device usage models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    Period,
    TimeStampedModel,
    Timing,
)

from . import choices


class DeviceUsageDerivedFromReference(BaseReference):
    """Device Usage Derived From Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="device_usage_derived_from_reference_identifier",
        null=True,
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_derived_from_reference_service_request",
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_derived_from_reference_procedure",
        null=True,
    )
    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_derived_from_reference_claim",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_derived_from_reference_observation",
        null=True,
    )
    # questionnaire_response = models.ForeignKey(
    #     "questionnaireresponses.QuestionnaireResponse",
    #     on_delete=models.DO_NOTHING,
    #     related_name="device_usage_derived_from_reference_questionnaire_response",
    #     null=True,
    # )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_derived_from_reference_document_reference",
        null=True,
    )


class DeviceUsageAdherence(TimeStampedModel):
    """Device Usage Adherence model."""

    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="device_usage_adherence_code",
        null=True,
    )
    reason = models.ManyToManyField(
        CodeableConcept, related_name="device_usage_adherence_reason", blank=True
    )


class DeviceUsageInformationSourceReference(BaseReference):
    """Device usage information source reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="device_usage_information_source_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_information_source_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_information_source_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_information_source_reference_practitioner_role",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_information_source_reference_related_person",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_information_source_reference_organization",
        null=True,
    )


class DeviceUsageReasonReference(BaseReference):
    """Device usage reason reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="device_usage_reason_reference_identifier",
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_reason_reference_condition",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_reason_reference_observation",
        null=True,
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_reason_reference_diagnostic_report",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_reason_reference_document_reference",
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_reason_reference_procedure",
        null=True,
    )


class DeviceUsageReasonCodeableReference(TimeStampedModel):
    """Device usage reason codeable reference model."""

    reference = models.ForeignKey(
        DeviceUsageReasonReference,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_usage_reason_codeable_reference_reference",
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="device_usage_reason_codeable_reference_concept",
    )


class DeviceUsage(TimeStampedModel):
    """Device usage model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="device_usages_identifier", blank=True
    )
    based_on = models.ManyToManyField(
        "servicerequests.ServiceRequestReference",
        related_name="device_usage_based_on",
        blank=True,
    )
    status = models.CharField(
        max_length=255,
        choices=choices.DeviceUsageStatus.choices,
        default=choices.DeviceUsageStatus.ACTIVE,
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="device_usage_category", blank=True
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_patient",
        null=True,
    )
    derived_from = models.ManyToManyField(
        DeviceUsageDerivedFromReference,
        related_name="device_usage_derived_from",
        blank=True,
    )
    context = models.ForeignKey(
        "encounters.EncounterEpisodeOfCareReference",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_context",
        null=True,
    )
    timing_timing = models.ForeignKey(
        Timing,
        on_delete=models.DO_NOTHING,
        related_name="device_usage_timing_timing",
        null=True,
    )
    timing_period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="device_usage_timing_period",
        null=True,
    )
    timing_date_time = models.DateTimeField(null=True)
    date_asserted = models.DateTimeField(null=True)
    usage_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="device_usage_usage_status",
        null=True,
    )
    usage_reason = models.ManyToManyField(
        CodeableConcept, related_name="device_usage_usage_reason", blank=True
    )
    adherence = models.ForeignKey(
        DeviceUsageAdherence,
        on_delete=models.DO_NOTHING,
        related_name="device_usage_adherence",
        null=True,
    )
    information_source = models.ForeignKey(
        DeviceUsageInformationSourceReference,
        on_delete=models.DO_NOTHING,
        related_name="device_usage_information_source",
        null=True,
    )
    device = models.ForeignKey(
        "devices.DeviceDeviceDefinitionCodeableReference",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_device",
        null=True,
    )
    reason = models.ManyToManyField(
        DeviceUsageReasonCodeableReference,
        related_name="device_usage_reason",
        blank=True,
    )
    body_site = models.ForeignKey(
        "bodystructures.BodyStructureCodeableReference",
        on_delete=models.DO_NOTHING,
        related_name="device_usage_body_site",
        null=True,
    )
    note = models.ManyToManyField(
        Annotation, related_name="device_usage_note", blank=True
    )
