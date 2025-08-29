"""body structure module."""

from django.db import models

from dfhir.base.models import (
    Attachment,
    BaseReference,
    CodeableConcept,
    Identifier,
    Quantity,
    TimeStampedModel,
)
from dfhir.imagingselections.models import ImagingSelectionReference


class DistanceFromLandmark(TimeStampedModel):
    """distance from landmark model."""

    device = models.ManyToManyField(
        "devices.DeviceCodeableReference",
        blank=True,
        related_name="distance_from_landmark_device",
    )
    value = models.ManyToManyField(
        Quantity, blank=True, related_name="distance_from_landmark_value"
    )


class BodyLandmarkOrientation(TimeStampedModel):
    """body landmark orientation model."""

    landmark_description = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="body_landmark_orientation_landmark_description",
    )
    clock_face_position = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="body_landmark_orientation_clock_face_position",
    )
    distance_from_landmark = models.ManyToManyField(
        DistanceFromLandmark,
        blank=True,
        related_name="body_landmark_orientation_distance_from_landmark",
    )
    surface_orientation = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="body_landmark_orientation_surface_orientation",
    )


class IncludedStructure(TimeStampedModel):
    """included structure model."""

    structure = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="included_structure_structure",
    )
    laterality = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="included_structure_laterality",
    )
    body_landmark_orientation = models.ManyToManyField(
        BodyLandmarkOrientation,
        blank=True,
        related_name="included_structure_body_landmark_orientation",
    )
    spatial_reference = models.ManyToManyField(
        ImagingSelectionReference,
        blank=True,
        related_name="included_structure_spatial_reference",
    )
    qualifier = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="included_structure_qualifier"
    )


# Create your models here.
class BodyStructure(TimeStampedModel):
    """body structure model."""

    identifier = models.ManyToManyField(
        Identifier,
        blank=True,
        related_query_name="body_structure_identifier",
    )
    active = models.BooleanField(default=True)
    morphology = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="body_structure_morphology",
    )
    included_structure = models.ManyToManyField(
        IncludedStructure, related_name="body_structure_included_structure", blank=True
    )
    excluded_structure = models.ManyToManyField(
        IncludedStructure, blank=True, related_name="body_structure_excluded_structure"
    )
    description = models.TextField(null=True)
    image = models.ManyToManyField(
        Attachment, blank=True, related_name="body_structure_image"
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="body_structure_patient",
    )


class BodyStructureReference(BaseReference):
    """body structure reference model."""

    identifier = models.ForeignKey(Identifier, on_delete=models.SET_NULL, null=True)
    body_structure = models.ForeignKey(
        BodyStructure, on_delete=models.SET_NULL, null=True
    )


class BodyStructureCodeableReference(TimeStampedModel):
    """body structure codeable reference model."""

    reference = models.ForeignKey(
        BodyStructureReference, on_delete=models.SET_NULL, null=True
    )
    concept = models.ForeignKey(CodeableConcept, on_delete=models.SET_NULL, null=True)
