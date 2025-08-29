"""Vision prescription models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    SimpleQuantity,
    TimeStampedModel,
)

from . import choices


class VisionPrescriptionBasedOnReference(BaseReference):
    """Vision Prescription Based On Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="vision_prescription_based_on_reference_identifier",
        null=True,
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        related_name="vision_prescription_based_on_reference_care_plan",
        null=True,
    )
    # request_orchestration = models.ForeignKey(
    #     "requestorchestrations.RequestOrchestration",
    #     on_delete=models.DO_NOTHING,
    #     related_name="vision_prescription_based_on_reference_request_orchestration",
    #     null=True,
    # )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.DO_NOTHING,
        related_name="vision_prescription_based_on_reference_nutrition_order",
        null=True,
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        related_name="vision_prescription_based_on_reference_service_request",
        null=True,
    )


class VisionPrescriptionLensSpecificationPrism(TimeStampedModel):
    """Vision Prescription Lens Specification Prism model."""

    base = models.CharField(
        max_length=255,
        choices=choices.VisionPrescriptionLensSpecificationPrismBaseChoices.choices,
        default=choices.VisionPrescriptionLensSpecificationPrismBaseChoices.UP,
    )
    amount = models.FloatField(null=True)


class VisionPrescriptionLensSpecification(TimeStampedModel):
    """Vision Prescription Lens Specification model."""

    product = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="vision_prescription_lens_specification_product",
        null=True,
    )
    eye = models.CharField(
        max_length=255,
        choices=choices.VisionPrescriptionLensSpecificationEyeChoices.choices,
        default=choices.VisionPrescriptionLensSpecificationEyeChoices.RIGHT,
    )
    sphere = models.FloatField(null=True)
    cylinder = models.FloatField(null=True)
    axis = models.FloatField(null=True)
    prism = models.ManyToManyField(
        VisionPrescriptionLensSpecificationPrism,
        related_name="vision_prescription_lens_specification_prism",
        blank=True,
    )
    add = models.FloatField(null=True)
    power = models.FloatField(null=True)
    back_curve = models.FloatField(null=True)
    diameter = models.FloatField(null=True)
    duration = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.DO_NOTHING,
        related_name="vision_prescription_lens_specification_duration",
        null=True,
    )
    color = models.CharField(max_length=255, null=True)
    brand = models.CharField(max_length=255, null=True)
    note = models.ManyToManyField(
        Annotation,
        related_name="vision_prescription_lens_specification_note",
        blank=True,
    )


class VisionPrescription(TimeStampedModel):
    """Vision prescription model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="vision_prescription_identifier",
        blank=True,
    )
    based_on = models.ManyToManyField(
        VisionPrescriptionBasedOnReference,
        related_name="vision_prescription_based_on",
        blank=True,
    )
    status = models.CharField(
        max_length=255,
        choices=choices.VisionPrescriptionStatusChoices.choices,
        default=choices.VisionPrescriptionStatusChoices.ACTIVE,
    )
    created = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        related_name="vision_prescription_patient",
        null=True,
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        related_name="vision_prescription_encounter",
        null=True,
    )
    date_written = models.DateTimeField(null=True)
    prescriber = models.ForeignKey(
        "practitioners.PractitionerPractitionerRoleReference",
        on_delete=models.DO_NOTHING,
        related_name="vision_prescription_prescriber",
        null=True,
    )
    lens_specification = models.ManyToManyField(
        VisionPrescriptionLensSpecification,
        related_name="vision_prescription_lens_specification",
        blank=True,
    )
