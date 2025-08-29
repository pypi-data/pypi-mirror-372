"""immunization recommendation models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    OrganizationReference,
    Reference,
    TimeStampedModel,
)
from dfhir.patients.models import PatientReference


class ImmunizationRecommendationRecommendationDateCriterion(TimeStampedModel):
    """immunization recommendation recommendation date criterion model."""

    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_recommendation_recommendation_date_criterion_code",
    )
    value = models.DateTimeField(null=True)


class ImmunizationRecommendationSupportingImmunizationReference(BaseReference):
    """immunization recommendation supporting immunization reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_recommendation_supporting_immunization_reference_identifier",
    )

    immunization = models.ForeignKey(
        "immunizations.Immunization",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_recommendation_supporting_immunization_reference_immunization",
    )
    immunization_evolution = models.ForeignKey(
        "immunizationevaluations.ImmunizationEvaluation",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_recommendation_supporting_immunization_reference_immunization_evolution",
    )


class ImmunizationRecommendationRecommendation(TimeStampedModel):
    """immunization recommendation recommendation model."""

    vaccine_code = models.ManyToManyField(
        CodeableConcept,
        related_name="immunization_recommendation_recommendation_vaccine_code",
        blank=True,
    )
    target_disease = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="immunization_recommendation_recommendation_target_disease",
    )
    contraindicated_vaccine_code = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="immunization_recommendation_recommendation_contraindicated_vaccine_code",
    )
    forecast_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="immunization_recommendation_recommendation_forecast_status",
        null=True,
    )
    forecast_reason = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="immunization_recommendation_recommendation_forecast_reason",
    )
    date_criterion = models.ManyToManyField(
        ImmunizationRecommendationRecommendationDateCriterion,
        blank=True,
        related_name="immunization_recommendation_recommendation_date_criterion",
    )
    description = models.TextField(null=True)
    series = models.CharField(max_length=255, null=True)
    dose_number = models.CharField(max_length=255, null=True)
    series_doses = models.CharField(max_length=255, null=True)
    supporting_information = models.ManyToManyField(
        ImmunizationRecommendationSupportingImmunizationReference,
        blank=True,
        related_name="immunization_recommendation_supporting_information",
    )
    supporting_patient_information = models.ManyToManyField(
        Reference,
        blank=True,
        related_name="immunization_recommendation_recommendation_supporting_patient_information",
    )


class ImmunizationRecommendation(TimeStampedModel):
    """immunization recommendation model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="immunization_recommendation_identifier"
    )
    patient = models.ForeignKey(
        PatientReference,
        on_delete=models.DO_NOTHING,
        related_name="immunization_recommendation_patient",
        null=True,
    )
    date = models.DateTimeField(null=True)
    authority = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_recommendation_authority",
    )
    recommendation = models.ManyToManyField(
        ImmunizationRecommendationRecommendation,
        blank=True,
        related_name="immunization_recommendation_recommendation",
    )
