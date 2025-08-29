"""imaging study models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)
from dfhir.imagingstudies.choices import ImagingStudyStatusChoices


class ImagingStudySubjectReference(BaseReference):
    """Imaging study subject reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_subject_reference",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_subject_reference",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_subject_reference",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_subject_reference",
        null=True,
    )


class ImagingStudyBasedOnReference(BaseReference):
    """Imaging study based on reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_based_on_reference",
        null=True,
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_based_on_reference",
        null=True,
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_based_on_reference",
        null=True,
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_based_on_reference",
        null=True,
    )
    appointment_response = models.ForeignKey(
        "appointmentresponses.AppointmentResponse",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_based_on_reference",
        null=True,
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_based_on_reference",
        null=True,
    )


class ImagingStudyProcedureReference(BaseReference):
    """Imaging study procedure reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_procedure_reference",
        null=True,
    )

    # TODO: plan_definition = models.ForeignKey(
    #     "plandefinitions.PlanDefinition",
    #     on_delete=models.DO_NOTHING,
    #     related_name="imaging_study_procedure_reference",
    #     null=True,
    # )

    # TODO: activity_definition = models.ForeignKey(
    #     "activitydefinitions.ActivityDefinition",
    #     on_delete=models.DO_NOTHING,
    #     related_name="imaging_study_procedure_reference",
    #     null=True,
    # )


class ImagingStudyReasonReference(BaseReference):
    """imaging study reason."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_reason",
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_reason",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_reason",
        null=True,
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_reason",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_reason",
        null=True,
    )


class ImagingStudySeriesPerformerActorReference(BaseReference):
    """imaging study series performer reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_performer_reference",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_performer_reference",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_performer_reference",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_performer_reference",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_performer_reference",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_performer_reference",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_performer_reference",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_performer_reference",
        null=True,
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_performer_reference",
        null=True,
    )


class ImagingStudySeriesPerformer(TimeStampedModel):
    """imaging study series performer."""

    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_performer_reference",
        null=True,
    )
    actor = models.ForeignKey(
        ImagingStudySeriesPerformerActorReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_study_series_performer_reference",
    )


class ImagingStudySeriesInstance(TimeStampedModel):
    """imaging study series instance model."""

    uid = models.CharField(max_length=255, null=False)
    sop_class = models.CharField(max_length=255, null=True)
    number = models.IntegerField(null=True)
    title = models.CharField(max_length=255, null=True)


class ImagingStudySeries(TimeStampedModel):
    """Imaging study series."""

    uid = models.CharField(max_length=255, null=True)
    number = models.IntegerField(null=True)
    modality = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_modality",
    )
    description = models.CharField(max_length=255, null=True)
    number_of_instances = models.IntegerField(null=True)
    endpoint = models.ManyToManyField(
        "endpoints.EndpointReference", related_name="imaging_study_series_endpoint"
    )
    body_site = models.ForeignKey(
        "bodystructures.BodyStructureCodeableReference",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_body_site",
    )
    laterality = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_series_laterality",
    )
    specimen = models.ManyToManyField(
        "specimens.SpecimenReference",
        blank=True,
        related_name="imaging_study_series_specimen",
    )
    started = models.DateTimeField(null=True)
    performer = models.ManyToManyField(
        ImagingStudySeriesPerformer,
        related_name="imaging_study_series_performer",
        blank=True,
    )
    instance = models.ManyToManyField(
        ImagingStudySeriesInstance,
        blank=True,
        related_name="imaging_study_series_instance",
    )


class ImagingStudy(TimeStampedModel):
    """imaging study model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="imaging_study_identifier", blank=True
    )
    status = models.CharField(
        max_length=255, null=True, choices=ImagingStudyStatusChoices.choices
    )
    modality = models.ManyToManyField(
        CodeableConcept, related_name="imaging_study_modality", blank=True
    )
    subject = models.ForeignKey(
        ImagingStudySubjectReference,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_subject",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_study_encounter",
    )
    started = models.DateTimeField(null=True)
    based_on = models.ManyToManyField(
        ImagingStudyBasedOnReference, related_name="imaging_study_based_on", blank=True
    )
    part_of = models.ManyToManyField(
        "procedures.ProcedureReference",
        related_name="imaging_study_part_of",
        blank=True,
    )
    referrer = models.ForeignKey(
        "practitioners.PractitionerPractitionerRoleReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_study_referrer",
    )
    endpoint = models.ManyToManyField(
        "endpoints.EndpointReference", related_name="imaging_study_endpoint", blank=True
    )
    procedure = models.ManyToManyField(
        ImagingStudyProcedureReference,
        related_name="imaging_study_procedure",
        blank=True,
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_study_location",
    )
    reason = models.ManyToManyField(
        ImagingStudyReasonReference, blank=True, related_name="imaging_study_reason"
    )
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="imaging_study_note"
    )
    description = models.CharField(max_length=255, null=True)
    number_of_series = models.IntegerField(null=True)
    number_of_instances = models.IntegerField(null=True)
    series = models.ManyToManyField(
        ImagingStudySeries, related_name="imaging_study_series", blank=True
    )


class ImagingStudyReference(BaseReference):
    """imaging selection reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="imaging_study_reference_identifier",
        null=True,
    )
    imaging_study = models.ForeignKey(
        ImagingStudy,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_study_reference_imaging_study",
    )
