"""Clinical impressions models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    Period,
    Reference,
    TimeStampedModel,
)

from . import choices


class ClinicalImpressionReference(BaseReference):
    """Clinical Impression reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="clinical_impression_reference_identifier",
        null=True,
    )
    clinical_impression = models.ForeignKey(
        "ClinicalImpression",
        on_delete=models.CASCADE,
        related_name="clinical_impression_reference_clinical_impression",
        null=True,
    )


class ClinicalImpressionFindingItemReference(BaseReference):
    """Clinical Impression Finding Item reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="clinical_impression_finding_item_reference_identifier",
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.CASCADE,
        related_name="clinical_impression_finding_item_reference_condition",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.CASCADE,
        related_name="clinical_impression_finding_item_reference_observation",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.CASCADE,
        related_name="clinical_impression_finding_item_reference_document_reference",
        null=True,
    )


class ClinicalImpressionFindingItemCodeableReference(TimeStampedModel):
    """Clinical Impression Finding Item Codeable Reference model."""

    reference = models.ForeignKey(
        ClinicalImpressionFindingItemReference,
        on_delete=models.CASCADE,
        related_name="clinical_impression_finding_item_codeable_reference_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="clinical_impression_finding_item_codeable_reference_concept",
        null=True,
    )


class ClinicalImpressionFinding(TimeStampedModel):
    """Clinical Impression Finding model."""

    item = models.ForeignKey(
        ClinicalImpressionFindingItemCodeableReference,
        on_delete=models.CASCADE,
        related_name="clinical_impression_finding_item",
        null=True,
    )
    basis = models.TextField(null=True)


class ClinicalImpression(TimeStampedModel):
    """Clinical Impression model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="clinical_impression_identifier",
        blank=True,
    )
    status = models.CharField(
        max_length=255, null=True, choices=choices.ClinicalImpressionStatus.choices
    )
    status_reason = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="clinical_impression_status_reason",
        null=True,
    )
    description = models.TextField(null=True)
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.CASCADE,
        related_name="clinical_impression_subject",
        null=True,
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.CASCADE,
        related_name="clinical_impression_encounter",
        null=True,
    )
    effective_date_time = models.DateTimeField(null=True)
    effective_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="clinical_impression_effective_period",
        null=True,
    )
    date = models.DateTimeField(null=True)
    performer = models.ForeignKey(
        "practitioners.PractitionerPractitionerRoleReference",
        on_delete=models.CASCADE,
        related_name="clinical_impression_performer",
        null=True,
    )
    previous = models.ForeignKey(
        "ClinicalImpressionReference",
        on_delete=models.CASCADE,
        related_name="clinical_impression_previous",
        null=True,
    )
    problem = models.ManyToManyField(
        "conditions.ConditionAllergyIntoleranceReference",
        related_name="clinical_impression_problem",
        blank=True,
    )
    change_pattern = models.ForeignKey(
        CodeableConcept,
        related_name="clinical_impression_change_pattern",
        on_delete=models.CASCADE,
        null=True,
    )
    protocol = ArrayField(models.URLField(), null=True)
    summary = models.TextField(null=True)
    finding = models.ManyToManyField(
        ClinicalImpressionFinding,
        related_name="clinical_impression_finding",
        blank=True,
    )
    prognosis_codeable_concept = models.ManyToManyField(
        CodeableConcept,
        related_name="clinical_impression_prognosis_codeable_concept",
        blank=True,
    )
    # prognosis_reference = models.ManyToManyField(
    #     "riskassessments.RiskAssessment",
    #     related_name="clinical_impression_prognosis_reference",
    #     blank=True,
    # )
    supporting_info = models.ManyToManyField(
        Reference,
        related_name="clinical_impression_supporting_info",
        blank=True,
    )
    note = models.ManyToManyField(
        Annotation,
        related_name="clinical_impression_note",
        blank=True,
    )
