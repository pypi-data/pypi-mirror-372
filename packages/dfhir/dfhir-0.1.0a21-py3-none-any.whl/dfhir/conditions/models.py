"""Models for Conditions."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)


class ConditionReference(BaseReference):
    """Condition Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="condition_reference_identifier",
        null=True,
    )
    condition = models.ForeignKey(
        "Condition",
        on_delete=models.DO_NOTHING,
        related_name="condition_reference",
        null=True,
    )


class ConditionCodeableReference(TimeStampedModel):
    """Condition Codeable Reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="condition_concept",
        null=True,
    )
    reference = models.ForeignKey(
        ConditionReference,
        on_delete=models.DO_NOTHING,
        related_name="condition_codeable_reference",
        null=True,
    )


class ConditionStageAssessmentReference(BaseReference):
    """condition stage assessment reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="condition_stage_assessment_reference_identifier",
        null=True,
    )
    clinical_impression = models.ForeignKey(
        "clinicalimpressions.ClinicalImpression",
        on_delete=models.DO_NOTHING,
        related_name="condition_stage_assessment_reference_clinical_impression",
        null=True,
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        related_name="condition_stage_assessment_reference_diagnostic_report",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        related_name="condition_stage_assessment_reference_observation",
        null=True,
    )


class ConditionStage(TimeStampedModel):
    """Condition Stage model."""

    summary = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="condition_stage_summary",
        null=True,
    )
    assessment = models.ManyToManyField(
        ConditionStageAssessmentReference,
        blank=True,
        related_name="condition_stage_assessment",
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="condition_stage_type",
        null=True,
    )


class ConditionRecorderReference(BaseReference):
    """condition recorder reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="condition_recorder_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="condition_recorder_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="condition_recorder_reference_practitioner_role",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="condition_recorder_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="condition_recorder_reference_related_person",
        null=True,
    )


class ConditionAsserterReference(BaseReference):
    """condition asserter reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="condition_asserter_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="condition_asserter_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="condition_asserter_reference_practitioner_role",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="condition_asserter_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="condition_asserter_reference_related_person",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        related_name="condition_asserter_reference_device",
        null=True,
    )


class Condition(TimeStampedModel):
    """Condition model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="condition_identifier",
        blank=True,
    )
    clinical_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="condition_clinical_status",
        null=True,
    )
    verification_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="condition_verification_status",
        null=True,
    )
    category = models.ManyToManyField(
        CodeableConcept,
        related_name="condition_category",
        blank=True,
    )
    severity = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="condition_severity",
        null=True,
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="condition_code",
        null=True,
    )
    body_site = models.ManyToManyField(
        CodeableConcept,
        related_name="condition_body_site",
        blank=True,
    )
    body_structure = models.ForeignKey(
        "bodystructures.BodyStructure",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="condition_body_structure",
    )
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.DO_NOTHING,
        related_name="condition_subject",
        null=True,
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        related_name="condition_encounter",
        null=True,
    )
    onset_date_time = models.DateTimeField(null=True)
    onset_age = models.ForeignKey(
        "base.Age",
        on_delete=models.DO_NOTHING,
        related_name="condition_onset_age",
        null=True,
    )
    onset_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        related_name="condition_onset_period",
        null=True,
    )
    onset_range = models.ForeignKey(
        "base.Range",
        on_delete=models.DO_NOTHING,
        related_name="condition_onset_range",
        null=True,
    )
    onset_string = models.CharField(max_length=255, null=True)
    abatement_date_time = models.DateTimeField(null=True)
    abatement_age = models.ForeignKey(
        "base.Age",
        on_delete=models.DO_NOTHING,
        related_name="condition_abatement_age",
        null=True,
    )
    abatement_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        related_name="condition_abatement_period",
        null=True,
    )
    abatement_range = models.ForeignKey(
        "base.Range",
        on_delete=models.DO_NOTHING,
        related_name="condition_abatement_range",
        null=True,
    )
    abatement_string = models.CharField(max_length=255, null=True)
    recorded_date = models.DateTimeField(null=True)
    recorder = models.ForeignKey(
        ConditionRecorderReference,
        on_delete=models.DO_NOTHING,
        related_name="condition_recorder",
        null=True,
    )
    asserter = models.ForeignKey(
        ConditionAsserterReference,
        on_delete=models.DO_NOTHING,
        related_name="condition_asserter",
        null=True,
    )
    stage = models.ManyToManyField(
        ConditionStage, related_name="condition_stage", blank=True
    )
    evidence = models.ManyToManyField(
        "base.CodeableReference", related_name="condition_evidence", blank=True
    )
    note = models.ManyToManyField(
        "base.Annotation", related_name="condition_note", blank=True
    )


class ConditionObservationReference(BaseReference):
    """Conditions Observation Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="condition_observation_reference_identifier",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        related_name="condition_observation_reference_observation",
        null=True,
    )
    condition = models.ForeignKey(
        Condition,
        on_delete=models.DO_NOTHING,
        related_name="condition_observation_reference_condition",
        null=True,
    )


class ConditionObservationCodeableReference(TimeStampedModel):
    """Condition Observation Codeable Reference model."""

    reference = models.ForeignKey(
        ConditionObservationReference,
        on_delete=models.DO_NOTHING,
        related_name="condition_observation_codeable_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="condition_observation_concept",
        null=True,
    )


class ConditionAllergyIntoleranceReference(BaseReference):
    """Condition Allergy Intolerance Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="condition_allergy_intolerance_reference_identifier",
        null=True,
    )
    condition = models.ForeignKey(
        Condition,
        on_delete=models.DO_NOTHING,
        related_name="condition_allergy_intolerance_reference_condition",
        null=True,
    )
    allergy_intolerance = models.ForeignKey(
        "allergyintolerances.AllergyIntolerance",
        on_delete=models.DO_NOTHING,
        related_name="condition_allergy_intolerance_reference_allergy_intolerance",
        null=True,
    )
