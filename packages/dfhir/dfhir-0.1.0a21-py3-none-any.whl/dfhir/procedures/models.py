"""Procedure models."""

from django.db import models

from dfhir.base.models import (
    Age,
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    OrganizationReference,
    Period,
    Range,
    Reference,
    TimeStampedModel,
    Timing,
)

from . import choices


class ProcedureReference(BaseReference):
    """Procedure Reference model."""

    procedure = models.ForeignKey(
        "Procedure",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reference",
        null=True,
    )
    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_reference_identifier",
        null=True,
    )


class ProcedureBasedOnReference(BaseReference):
    """Procedure Based On Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_based_on_reference_identifier",
        null=True,
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        related_name="procedure_based_on_reference_care_plan",
        null=True,
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        related_name="procedure_based_on_reference_service_request",
        null=True,
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.DO_NOTHING,
        related_name="procedure_based_on_reference_medication_request",
        null=True,
    )


class ProcedurePartOfReference(BaseReference):
    """Procedure PartOf Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_partof_reference_identifier",
        null=True,
    )
    procedure = models.ForeignKey(
        "Procedure",
        on_delete=models.DO_NOTHING,
        related_name="procedure_partof_reference_procedure",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        related_name="procedure_partof_reference_observation",
        null=True,
    )
    medication_administration = models.ForeignKey(
        "medicationadministrations.MedicationAdministration",
        on_delete=models.DO_NOTHING,
        related_name="procedure_partof_reference_medication_administration",
        null=True,
    )


class ProcedureSubjectReference(BaseReference):
    """Procedure Subject Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_subject_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="procedure_subject_reference_patient",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        related_name="procedure_subject_reference_group",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        related_name="procedure_subject_reference_device",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="procedure_subject_reference_organization",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="procedure_subject_reference_practitioner",
        null=True,
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.DO_NOTHING,
        related_name="procedure_subject_reference_location",
        null=True,
    )


class ProcedureFocusReference(BaseReference):
    """Procedure focus reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_focus_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="procedure_focus_reference_patient",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        related_name="procedure_focus_reference_group",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="procedure_focus_reference_related_person",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="procedure_focus_reference_practitioner",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="procedure_focus_reference_organization",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        related_name="procedure_focus_reference_care_team",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="procedure_focus_reference_practitioner_role",
        null=True,
    )
    specimen = models.ForeignKey(
        "specimens.Specimen",
        on_delete=models.DO_NOTHING,
        related_name="procedure_focus_reference_specimen",
        null=True,
    )


class ProcedureRecorderReference(BaseReference):
    """Procedure Recorder Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_recorder_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="procedure_recorder_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="procedure_recorder_reference_related_person",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="procedure_recorder_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="procedure_recorder_reference_practitioner_role",
        null=True,
    )


class ProcedurePerformerActorReference(BaseReference):
    """Procedure Performer Actor Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_actor_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_actor_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_actor_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_actor_reference_organization",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_actor_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_actor_reference_related_person",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_actor_reference_device",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_actor_reference_care_team",
        null=True,
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_actor_reference_healthcare_service",
        null=True,
    )


class ProcedureReasonReference(BaseReference):
    """Procedure Reason Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_reason_reference_identifier",
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reason_reference_condition",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reason_reference_observation",
        null=True,
    )
    procedure = models.ForeignKey(
        "Procedure",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reason_reference_procedure",
        null=True,
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reason_reference_diagnostic_report",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reason_reference_document_reference",
        null=True,
    )


class ProcedureReasonCodeableReference(TimeStampedModel):
    """Procedure Reason Codeable Reference model."""

    reference = models.ForeignKey(
        ProcedureReasonReference,
        on_delete=models.DO_NOTHING,
        related_name="procedure_reason_codeable_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="procedure_reason_concept",
        null=True,
    )


class ProcedureUsedReference(BaseReference):
    """Procedure Used Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_used_reference_identifier",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        related_name="procedure_used_reference_device",
        null=True,
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.DO_NOTHING,
        related_name="procedure_used_reference_medication",
        null=True,
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        related_name="procedure_used_reference_substance",
        null=True,
    )
    biologically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.DO_NOTHING,
        related_name="procedure_used_reference_biologically_derived_product",
        null=True,
    )


class ProcedureUsedCodeableReference(TimeStampedModel):
    """Procedure Used Codeable Reference model."""

    reference = models.ForeignKey(
        ProcedureUsedReference,
        on_delete=models.DO_NOTHING,
        related_name="procedure_used_codeable_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="procedure_used_concept",
        null=True,
    )


class ProcedureReportedReference(BaseReference):
    """Procedure Reported Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_reported_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reported_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reported_reference_related_person",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reported_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reported_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reported_reference_organization",
        null=True,
    )


class ProcedurePerformer(TimeStampedModel):
    """Procedure Performer model."""

    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_function",
        null=True,
    )
    actor = models.ForeignKey(
        ProcedurePerformerActorReference,
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_actor",
        null=True,
    )
    on_behalf_of = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_on_behalf_of",
        null=True,
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="procedure_performer_period",
        null=True,
    )


class ProcedureFocalDevice(TimeStampedModel):
    """Procedure Focal Device model."""

    action = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="procedure_focal_device_action",
        null=True,
    )
    manipulated = models.ForeignKey(
        "devices.DeviceReference",
        on_delete=models.DO_NOTHING,
        related_name="procedure_focal_device_manipulated",
        null=True,
    )


class ProcedureReportReference(BaseReference):
    """Procedure Report Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="procedure_report_reference_identifier",
        null=True,
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reported_reference_diagnostic_report",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        related_name="procedure_reported_reference_document_reference",
        null=True,
    )
    # composition = models.ForeignKey(
    #     "compositions.Composition",
    #     on_delete=models.DO_NOTHING,
    #     related_name="procedure_reported_reference_composition",
    #     null=True,
    # )


class Procedure(TimeStampedModel):
    """Procedure model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="procedure_identifier",
        blank=True,
    )
    based_on = models.ManyToManyField(
        ProcedureBasedOnReference, blank=True, related_name="procedure_based_on"
    )
    part_of = models.ManyToManyField(
        ProcedurePartOfReference, blank=True, related_name="procedure_part_of"
    )
    status = models.CharField(
        max_length=255, choices=choices.ProcedureStatus.choices, null=True
    )
    status_reason = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="procedure_status_reason",
        null=True,
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="procedure_category", blank=True
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="procedure_code",
        null=True,
    )
    subject = models.ForeignKey(
        ProcedureSubjectReference,
        on_delete=models.DO_NOTHING,
        related_name="procedure_subject",
        null=True,
    )
    focus = models.ForeignKey(
        ProcedureFocusReference,
        on_delete=models.DO_NOTHING,
        related_name="procedure_focus",
        null=True,
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        related_name="procedure_encounter",
        null=True,
    )
    occurrence_date_time = models.DateTimeField(null=True)
    occurrence_period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        related_name="procedure_occurrence_period",
        null=True,
    )
    occurrence_string = models.CharField(max_length=255, null=True)
    occurrence_age = models.ForeignKey(
        Age,
        on_delete=models.DO_NOTHING,
        related_name="procedure_occurrence_age",
        null=True,
    )
    occurrence_range = models.ForeignKey(
        Range,
        on_delete=models.DO_NOTHING,
        related_name="procedure_occurrence_range",
        null=True,
    )
    occurrence_timing = models.ForeignKey(
        Timing,
        on_delete=models.DO_NOTHING,
        related_name="procedure_occurrence_timing",
        null=True,
    )
    recorded = models.DateTimeField(null=True)
    recorder = models.ForeignKey(
        ProcedureRecorderReference,
        on_delete=models.DO_NOTHING,
        related_name="procedure_recorder",
        null=True,
    )
    reported_boolean = models.BooleanField(null=True)
    reported_reference = models.ForeignKey(
        ProcedureReportedReference,
        on_delete=models.DO_NOTHING,
        related_name="procedure_reported_reference",
        null=True,
    )
    performer = models.ManyToManyField(
        ProcedurePerformer, blank=True, related_name="procedure_performer"
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        related_name="procedure_location",
        null=True,
    )
    reason = models.ManyToManyField(
        ProcedureReasonCodeableReference, blank=True, related_name="procedure_reason"
    )
    body_site = models.ManyToManyField(
        CodeableConcept,
        related_name="procedure_body_site",
        blank=True,
    )
    body_structure = models.ManyToManyField(
        "bodystructures.BodyStructureReference",
        related_name="procedure_body_structure",
        blank=True,
    )
    outcome = models.ManyToManyField(
        "observations.ObservationCodeableReference",
        related_name="procedure_outcome",
        blank=True,
    )
    report = models.ManyToManyField(
        ProcedureReportReference,
        related_name="procedure_report",
        blank=True,
    )
    complication = models.ManyToManyField(
        "conditions.ConditionCodeableReference",
        related_name="procedure_complication",
        blank=True,
    )
    follow_up = models.ManyToManyField(
        "servicerequests.ServiceRequestPlanDefinitionReference",
        related_name="procedure_follow_up",
        blank=True,
    )
    note = models.ManyToManyField(
        Annotation,
        related_name="procedure_note",
        blank=True,
    )
    focal_device = models.ManyToManyField(
        ProcedureFocalDevice, blank=True, related_name="procedure_focal_device"
    )
    used = models.ManyToManyField(
        ProcedureUsedCodeableReference, blank=True, related_name="procedure_used"
    )
    supporting_info = models.ManyToManyField(
        Reference, blank=True, related_name="procedure_supporting_info"
    )


class ProcedureCodeableReference(TimeStampedModel):
    """Procedure Codeable Reference model."""

    reference = models.ForeignKey(
        ProcedureReference,
        on_delete=models.DO_NOTHING,
        related_name="procedure_codeable_reference_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="procedure_codeable_reference_concept",
        null=True,
    )
