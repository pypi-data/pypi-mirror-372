"""immunization evaluations models."""

from django.db import models

from dfhir.base.models import Identifier, TimeStampedModel
from dfhir.immunizationevaluations.choices import ImmunizationEvaluationStatusChoices


class ImmunizationEvaluation(TimeStampedModel):
    """Immunization Evaluation model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="immunization_evaluation_identifier"
    )
    status = models.CharField(
        max_length=255, choices=ImmunizationEvaluationStatusChoices.choices, null=True
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_evaluation_patient",
    )
    date = models.DateTimeField(null=True)
    authority = models.ForeignKey(
        "base.OrganizationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_evaluation_authority",
    )
    target_disease = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_evaluation_target_disease",
    )
    immunization_event = models.ForeignKey(
        "immunizations.ImmunizationReference",
        on_delete=models.DO_NOTHING,
        related_name="immunization_evaluation_immunization_event",
        null=True,
    )
    dose_status = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_evaluation_dose_status",
    )
    dose_status_reason = models.ManyToManyField(
        "base.CodeableConcept",
        related_name="immunization_evaluation_dose_status_reason",
        blank=True,
    )
    description = models.TextField(null=True)
    series = models.CharField(max_length=255, null=True)
    dose_number = models.CharField(max_length=255, null=True)
    series_doses = models.CharField(max_length=255, null=True)
