"""risk assessment models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Reference,
    TimeStampedModel,
)
from dfhir.riskassessments.choices import RiskAssessmentStatusChoices


class RiskAssessmentPrediction(TimeStampedModel):
    """risk assessment prediction."""

    outcome = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_predictions_outcome",
    )
    probability_decimal = models.DecimalField(
        max_digits=10, decimal_places=10, null=True
    )
    probability_range = models.ForeignKey(
        "base.Range",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_predictions_probability_range",
    )
    qualitative_risk = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_predictions_qualitative_risk",
    )
    relative_risk = models.DecimalField(max_digits=10, decimal_places=10, null=True)
    when_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_predictions_when_period",
    )
    when_range = models.ForeignKey(
        "base.Range",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_predictions_when_range",
    )
    rationale = models.TextField(null=True)


class RiskAssessmentPerformerReference(BaseReference):
    """risk assessment performer reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_performer_references_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_performer_references_patient",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_performer_references_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_performer_references_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_performer_references_related_person",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_performer_references_device",
    )


class RiskAssessmentReasonReference(BaseReference):
    """risk assessment reason reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_reason_references_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_reason_references_condition",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_reason_references_observation",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_reason_references_diagnostic_report",
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_reason_references_document_reference",
    )


class RiskAssessmentReasonCodeableConcept(TimeStampedModel):
    """risk assessment reason codeable concept."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_reason_codeable_concepts_code",
    )
    reference = models.ForeignKey(
        RiskAssessmentReasonReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessment_reason_codeable_concepts_reference",
    )


class RiskAssessment(TimeStampedModel):
    """risk assessment model."""

    identifier = models.ManyToManyField(
        Identifier,
        blank=True,
        related_name="risk_assessments_identifier",
    )
    based_on = models.ForeignKey(
        Reference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessments_based_on",
    )
    parent = models.ForeignKey(
        Reference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessments_parent",
    )
    status = models.CharField(
        max_length=200, null=True, choices=RiskAssessmentStatusChoices.choices
    )
    method = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessments_method",
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessments_code",
    )
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessments_subject",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessments_encounter",
    )
    occurrence_date_time = models.DateTimeField(null=True)
    occurrence_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessments_occurrence_period",
    )
    condition = models.ForeignKey(
        "conditions.ConditionReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessments_condition",
    )
    performer = models.ForeignKey(
        RiskAssessmentPerformerReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="risk_assessments_performer",
    )
    reason = models.ManyToManyField(
        RiskAssessmentReasonCodeableConcept,
        blank=True,
        related_name="risk_assessments_reason",
    )
    basis = models.ManyToManyField(
        Reference,
        blank=True,
        related_name="risk_assessments_basis",
    )
    prediction = models.ManyToManyField(
        RiskAssessmentPrediction, related_name="risk_assessments_prediction", blank=True
    )
    mitigation = models.CharField(max_length=200, null=True)
    note = models.ManyToManyField(
        "base.Annotation", related_name="risk_assessments_note", blank=True
    )
