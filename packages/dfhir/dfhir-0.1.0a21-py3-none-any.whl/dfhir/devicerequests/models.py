"""Devicerequests models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    Period,
    Quantity,
    Range,
    Reference,
    TimeStampedModel,
    Timing,
)

# from dfhir.coverages.models import CoverageClaimReference
# from dfhir.devices.models import DeviceDeviceDefinitionCodeableReference
from dfhir.provenances.models import ProvenanceReference

from . import choices


class DeviceRequestParameter(TimeStampedModel):
    """Device request parameter model."""

    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_parameter_code",
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_parameter_value_codeable_concept",
    )
    value_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_parameter_value_quantity",
    )
    value_range = models.ForeignKey(
        Range,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_parameter_value_range",
    )
    value_boolean = models.BooleanField(default=False)


class DeviceRequestSubjectReference(BaseReference):
    """Device request subject reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_subject_reference_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_subject_reference_patient",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_subject_reference_group",
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_subject_reference_location",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_subject_reference_device",
    )


class DeviceRequestRequesterReference(BaseReference):
    """Device request requester reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_requester_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_requester_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_requester_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_requester_reference_organization",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_requester_reference_device",
    )


class DeviceRequestRequesterCodeableReference(TimeStampedModel):
    """Device request requester codeable reference model."""

    reference = models.ForeignKey(
        DeviceRequestRequesterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_requester_codeable_reference_reference",
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_requester_codeable_reference_code",
    )


class DeviceRequestReasonReference(BaseReference):
    """Device request reason reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_reason_reference_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_reason_reference_condition",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_reason_reference_observation",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_reason_reference_diagnostic_report",
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_reason_reference_document_reference",
    )


class DeviceRequestReasonCodeableReference(TimeStampedModel):
    """Device request reason codeable reference model."""

    reference = models.ForeignKey(
        DeviceRequestReasonReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_reason_codeable_reference_reference",
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_reason_codeable_reference_concept",
    )


class DeviceRequestPerformerReference(BaseReference):
    """Device request performer reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_reference_organization",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_reference_care_team",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthCareService",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_reference_healthcare_service",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_reference_patient",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_reference_device",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_reference_related_person",
    )


class DeviceRequestPerformerCodeableReference(TimeStampedModel):
    """Device request performer codeable reference model."""

    reference = models.ForeignKey(
        DeviceRequestPerformerReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_codeable_reference_reference",
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer_codeable_reference_concept",
    )


class DeviceRequest(TimeStampedModel):
    """Device request model."""

    identifier = models.ManyToManyField(
        Identifier,
        blank=True,
        related_name="device_request_identifier",
    )
    # instantiates_canonical = models.ForeignKey(
    #     ActivityDefinitionPlanDefinitionCanonical,
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="device_request_instantiates_canonical",
    # )
    instantiates_uri = ArrayField(models.URLField(), null=True)
    based_on = models.ManyToManyField(
        Reference,
        related_name="device_request_based_on",
        blank=True,
    )
    replaces = models.ManyToManyField(
        "DeviceRequestReference",
        related_name="device_request_replaces",
        blank=True,
    )
    group_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_group_identifier",
    )

    status = models.CharField(
        max_length=255,
        choices=choices.DeviceRequestStatus.choices,
        default=choices.DeviceRequestStatus.ACTIVE,
    )
    intent = models.CharField(
        max_length=255,
        choices=choices.DeviceRequestIntent.choices,
        default=choices.DeviceRequestIntent.ORDER,
    )
    priority = models.CharField(
        max_length=255,
        choices=choices.DeviceRequestPriority.choices,
        default=choices.DeviceRequestPriority.ROUTINE,
    )
    do_not_perform = models.BooleanField(default=False)
    code = models.ForeignKey(
        "devices.DeviceDeviceDefinitionCodeableReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_code",
    )
    quantity = models.IntegerField(null=True)
    parameter = models.ManyToManyField(
        DeviceRequestParameter, related_name="device_request_parameter", blank=True
    )
    subject = models.ForeignKey(
        DeviceRequestSubjectReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_subject",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_encounter",
    )
    occurrence_datetime = models.DateTimeField(null=True)
    occurrence_period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_occurrence_period",
    )
    occurrence_timing = models.ForeignKey(
        Timing,
        on_delete=models.CASCADE,
        related_name="device_request_occurrence_timing",
        null=True,
    )
    authored_on = models.DateTimeField(null=True)
    requester = models.ForeignKey(
        DeviceRequestRequesterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_requester",
    )
    performer = models.ForeignKey(
        DeviceRequestPerformerCodeableReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_performer",
    )
    reason = models.ManyToManyField(
        DeviceRequestReasonCodeableReference,
        related_name="device_request_reason",
        blank=True,
    )
    as_needed = models.BooleanField(default=False)
    as_needed_for = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_as_needed_for",
    )
    # insurance = models.ManyToManyField(
    #     CoverageClaimReference,
    #     related_name="device_request_insurance",
    #     blank=True,
    # )
    supporting_info = models.ManyToManyField(
        Reference,
        related_name="device_request_supporting_info",
        blank=True,
    )
    note = models.ManyToManyField(
        Annotation,
        related_name="device_request_note",
        blank=True,
    )
    relevant_history = models.ManyToManyField(
        ProvenanceReference,
        related_name="device_request_relevant_history",
        blank=True,
    )


class DeviceRequestReference(BaseReference):
    """Device request reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_reference_identifier",
    )
    device_request = models.ForeignKey(
        DeviceRequest,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="device_request_reference_device_request",
    )
