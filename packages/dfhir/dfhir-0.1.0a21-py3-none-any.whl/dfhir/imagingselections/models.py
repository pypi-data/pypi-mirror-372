"""image selection models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)

from .choices import (
    ImagingSelectionInstanceImageRegion2DRegionTypeChoices,
    ImagingSelectionInstanceImageRegion3DRegionTypeChoices,
    ImagingSelectionStatusChoices,
)

# Create your models here.


class ImagingSelectionPerformerActorReference(BaseReference):
    """imaging selection actor reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_actor_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_actor_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_actor_reference_practitioner_role",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_actor_reference_device",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_actor_reference_organization",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeamReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_actor_reference_care_team",
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_actor_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_actor_reference_related_person",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_actor_reference_healthcare_service",
    )


class ImagingSelectionPerformer(TimeStampedModel):
    """imaging selection performer model."""

    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="imaging_selection_performer_function",
        null=True,
    )
    actor = models.ForeignKey(
        ImagingSelectionPerformerActorReference,
        on_delete=models.DO_NOTHING,
        related_name="imaging_selection_performer_actor",
        null=True,
    )


class ImagingSelectionBasedOnReference(BaseReference):
    """image selection based on reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_based_on_reference_identifier",
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_based_on_reference_care_plan",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_based_on_reference_service_request",
    )
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_based_on_reference_appointment",
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_based_on_reference_task",
    )


class ImagingSelectionInstanceImagingRegion2D(TimeStampedModel):
    """image selection instance imaging region 2d model."""

    region_type = models.CharField(
        max_length=255,
        null=True,
        choices=ImagingSelectionInstanceImageRegion2DRegionTypeChoices.choices,
    )
    coordinate = ArrayField(models.FloatField(null=True), null=True)


class ImagingSelectionInstance(TimeStampedModel):
    """imaging selection instance model."""

    uid = models.CharField(max_length=255, null=True)
    number = models.IntegerField(null=True)
    sop_class = models.CharField(max_length=255, null=True)
    subset = ArrayField(models.CharField(max_length=255, null=True), null=True)
    imaging_region_2d = models.ManyToManyField(
        ImagingSelectionInstanceImagingRegion2D,
        blank=True,
        related_name="image_selection_instance_imaging_region_2d",
    )


class ImagingSelectionImageRegion3D(TimeStampedModel):
    """image selection image region 3d model."""

    region_type = models.CharField(
        max_length=255,
        null=True,
        choices=ImagingSelectionInstanceImageRegion3DRegionTypeChoices.choices,
    )
    coordinate = ArrayField(models.FloatField(null=True), null=True)


class ImagingSelectionSubjectReference(BaseReference):
    """imaging selection subject reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_subject_reference_identifier",
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_subject_reference_patient",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_subject_reference_group",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_subject_reference_device",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_subject_reference_procedure",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_subject_reference_practitioner",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_subject_reference_medication",
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_subject_reference_substance",
    )
    specimen = models.ForeignKey(
        "specimens.Specimen",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="imaging_selection_subject_reference_specimen",
    )


class ImagingSelection(TimeStampedModel):
    """image selection model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="image_selection_identifier"
    )
    status = models.CharField(
        max_length=255, null=True, choices=ImagingSelectionStatusChoices.choices
    )
    category = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="image_selection_category"
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_code",
    )
    subject = models.ForeignKey(
        ImagingSelectionSubjectReference,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="image_selection_subject",
    )
    issued = models.DateTimeField(null=True)
    performer = models.ManyToManyField(
        ImagingSelectionPerformer, blank=True, related_name="image_selection_performer"
    )
    based_on = models.ManyToManyField(
        ImagingSelectionBasedOnReference,
        blank=True,
        related_name="image_selection_based_on",
    )
    derived_from = models.ForeignKey(
        "imagingstudies.ImagingStudyReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_derived_from",
    )
    study_uid = models.CharField(max_length=255, null=True)
    series_uid = models.CharField(max_length=255, null=True)
    series_number = models.IntegerField(null=True)
    frame_of_reference_uid = models.CharField(max_length=255, null=True)
    body_site = models.ManyToManyField(
        "bodystructures.BodyStructureCodeableReference",
        blank=True,
        related_name="imaging_selection_bodysite",
    )
    focus = models.ManyToManyField(
        "ImagingSelectionReference", blank=True, related_name="imaging_selection_focus"
    )
    endpoint = models.ManyToManyField(
        "endpoints.EndpointReference",
        blank=True,
        related_name="imaging_selection_endpoint",
    )
    instance = models.ManyToManyField(
        ImagingSelectionInstance, blank=True, related_name="image_selection_instance"
    )
    image_region_3d = models.ManyToManyField(
        ImagingSelectionImageRegion3D,
        blank=True,
        related_name="image_selection_image_region_3d",
    )


class ImagingSelectionReference(BaseReference):
    """image selection reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_reference_identifier",
    )
    image_selection = models.ForeignKey(
        ImagingSelection,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_reference_image_selection",
    )


class ImagingSelectionCodeableReference(TimeStampedModel):
    """image selection codeable reference model."""

    concept = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        ImagingSelectionReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="image_selection_codeable_reference_reference",
    )
