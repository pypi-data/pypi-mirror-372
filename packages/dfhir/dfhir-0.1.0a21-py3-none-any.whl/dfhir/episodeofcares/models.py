"""Model for EpisodeOfCare."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    OrganizationReference,
    Period,
    TimeStampedModel,
)

from . import choices


class EpisodeOfCareStatusHistory(TimeStampedModel):
    """Model for EpisodeOfCareStatusHistory."""

    status = models.CharField(
        max_length=255, choices=choices.EpisodeOfCareStatusChoices.choices, null=True
    )
    period = models.ForeignKey(
        Period,
        related_name="episode_of_care_status_history_period",
        on_delete=models.CASCADE,
        null=True,
    )


class EpisodeOfCareReasonValueReference(BaseReference):
    """Reference to an EpisodeOfCareReasonValue."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="episode_of_care_reason_value_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        related_name="episode_of_care_reason_value_reference_condition",
        on_delete=models.CASCADE,
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        related_name="episode_of_care_reason_value_reference_procedure",
        on_delete=models.CASCADE,
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        related_name="episode_of_care_reason_value_reference_observation",
        on_delete=models.CASCADE,
        null=True,
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthCareService",
        related_name="episode_of_care_reason_value_reference_healthcare_service",
        on_delete=models.CASCADE,
        null=True,
    )


class EpisodeOfCareReasonValueCodeableReference(TimeStampedModel):
    """Model for EpisodeOfCareReasonValueCodeableReference."""

    reference = models.ForeignKey(
        EpisodeOfCareReasonValueReference,
        related_name="episode_of_care_reason_value_codeable_reference_reference",
        on_delete=models.CASCADE,
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        related_name="episode_of_care_reason_value_codeable_reference_concept",
        on_delete=models.CASCADE,
        null=True,
    )


class EpisodeOfCareReason(TimeStampedModel):
    """Model for EpisodeOfCareReason."""

    use = models.ForeignKey(
        CodeableConcept,
        related_name="episode_of_care_reason_use",
        on_delete=models.CASCADE,
        null=True,
    )
    value = models.ForeignKey(
        EpisodeOfCareReasonValueCodeableReference,
        related_name="episode_of_care_reason_value",
        on_delete=models.CASCADE,
        null=True,
    )


class EpisodeOfCareDiagnosis(TimeStampedModel):
    """Model for EpisodeOfCareDiagnosis."""

    condition = models.ForeignKey(
        "conditions.ConditionCodeableReference",
        related_name="episode_of_care_diagnosis_condition",
        on_delete=models.CASCADE,
        null=True,
    )
    use = models.ForeignKey(
        CodeableConcept,
        related_name="episode_of_care_diagnosis_use",
        on_delete=models.CASCADE,
        null=True,
    )


class EpisodeOfCare(TimeStampedModel):
    """Model for EpisodeOfCare."""

    identifier = models.ManyToManyField(
        Identifier, related_name="episode_of_care_identifier", blank=True
    )
    status = models.CharField(
        max_length=255, choices=choices.EpisodeOfCareStatusChoices.choices, null=True
    )
    status_history = models.ManyToManyField(
        EpisodeOfCareStatusHistory,
        related_name="episode_of_care_status_history",
        blank=True,
    )
    type = models.ManyToManyField(
        CodeableConcept, related_name="episode_of_care_type", blank=True
    )
    diagnosis = models.ManyToManyField(
        EpisodeOfCareDiagnosis, related_name="episode_of_care_diagnosis", blank=True
    )
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        related_name="episode_of_care_patient",
        on_delete=models.CASCADE,
    )
    managing_organization = models.ForeignKey(
        OrganizationReference,
        related_name="episode_of_care_managing_organization",
        on_delete=models.CASCADE,
    )
    period = models.ForeignKey(
        Period,
        related_name="episode_of_care_period",
        on_delete=models.CASCADE,
        null=True,
    )
    referral_request = models.ManyToManyField(
        "servicerequests.ServiceRequestReference",
        related_name="episode_of_care_referral_request",
        blank=True,
    )
    care_manager = models.ForeignKey(
        "practitioners.PractitionerPractitionerRoleReference",
        related_name="episode_of_care_care_manager",
        on_delete=models.CASCADE,
        null=True,
    )
    care_team = models.ManyToManyField(
        "careteams.CareTeamReference",
        related_name="episode_of_care_care_team",
        blank=True,
    )
    account = models.ManyToManyField(
        "accounts.AccountReference", related_name="episode_of_care_account", blank=True
    )


class EpisodeOfCareReference(BaseReference):
    """Reference to an EpisodeOfCare."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="episode_of_care_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    episode_of_care = models.ForeignKey(
        EpisodeOfCare,
        related_name="episode_of_care_reference_episode_of_care",
        on_delete=models.CASCADE,
        null=True,
    )
