"""Family member history models."""

from django.db import models

from dfhir.base.models import (
    Age,
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    Period,
    Range,
    TimeStampedModel,
)

from . import choices


class FamilyMemberHistoryParticipantActorReference(BaseReference):
    """Family Member History Participant Actor Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="family_member_history_participant_actor_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="family_member_history_participant_actor_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="family_member_history_participant_actor_reference_practitioner_role",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="family_member_history_participant_actor_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="family_member_history_participant_actor_reference_related_person",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="family_member_history_participant_actor_reference_device",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="family_member_history_participant_actor_reference_organization",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.CASCADE,
        related_name="family_member_history_participant_actor_reference_care_team",
        null=True,
    )


class FamilyMemberHistoryParticipant(TimeStampedModel):
    """Family Member History Participant model."""

    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="family_member_history_participant_function",
        null=True,
    )
    actor = models.ForeignKey(
        FamilyMemberHistoryParticipantActorReference,
        on_delete=models.CASCADE,
        related_name="family_member_history_participant_actor",
    )


class FamilyMemberHistoryReasonReference(BaseReference):
    """Family Member History Reason Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="family_member_history_reason_reference_identifier",
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.CASCADE,
        related_name="family_member_history_reason_reference_condition",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.CASCADE,
        related_name="family_member_history_reason_reference_observation",
        null=True,
    )
    allergy_intolerance = models.ForeignKey(
        "allergyintolerances.AllergyIntolerance",
        on_delete=models.CASCADE,
        related_name="family_member_history_reason_reference_allergy_intolerance",
        null=True,
    )
    # questionnaire_response = models.ForeignKey(
    #     "questionnaireresponses.QuestionnaireResponse",
    #     on_delete=models.CASCADE,
    #     related_name="family_member_history_reason_reference_questionnaire_response",
    #     null=True,
    # )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.CASCADE,
        related_name="family_member_history_reason_reference_diagnostic_report",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.CASCADE,
        related_name="family_member_history_reason_reference_document_reference",
        null=True,
    )


class FamilyMemberHistoryReasonCodeableReference(TimeStampedModel):
    """Family Member History Reason Codeable Reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="family_member_history_reason_codeable_reference_codeable_concept",
        null=True,
    )
    reference = models.ForeignKey(
        FamilyMemberHistoryReasonReference,
        on_delete=models.CASCADE,
        related_name="family_member_history_reason_codeable_reference_reference",
        null=True,
    )


class FamilyMemberHistoryCondition(TimeStampedModel):
    """Family Member History Condition model."""

    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="family_member_history_condition_code",
        null=True,
    )
    outcome = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="family_member_history_condition_outcome",
        null=True,
    )
    contributed_to_death = models.BooleanField(null=True)
    onset_age = models.ForeignKey(
        Age,
        on_delete=models.CASCADE,
        related_name="family_member_history_condition_onset_age",
        null=True,
    )
    onset_range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        related_name="family_member_history_condition_onset_range",
        null=True,
    )
    onset_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="family_member_history_condition_onset_period",
        null=True,
    )
    onset_string = models.CharField(max_length=255, null=True)
    note = models.ManyToManyField(
        Annotation, related_name="family_member_history_condition_note", blank=True
    )


class FamilyMemberHistoryProcedure(TimeStampedModel):
    """Family Member History Procedure model."""

    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="family_member_history_procedure_code",
        null=True,
    )
    outcome = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="family_member_history_procedure_outcome",
        null=True,
    )
    contributed_to_death = models.BooleanField(null=True)
    performed_age = models.ForeignKey(
        Age,
        on_delete=models.CASCADE,
        related_name="family_member_history_procedure_performed_age",
        null=True,
    )
    performed_range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        related_name="family_member_history_procedure_performed_range",
        null=True,
    )
    performed_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="family_member_history_procedure_performed_period",
        null=True,
    )
    performed_string = models.CharField(max_length=255, null=True)
    performed_date_time = models.DateTimeField(null=True)
    note = models.ManyToManyField(
        Annotation, related_name="family_member_history_procedure_note", blank=True
    )


class FamilyMemberHistory(TimeStampedModel):
    """Family Member History model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="family_member_history_identifier",
        blank=True,
    )
    status = models.CharField(
        max_length=255, choices=choices.FamilyMemberHistoryStatus.choices
    )
    data_absent_reason = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="family_member_history_data_absent_reason",
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.CASCADE,
        related_name="family_member_history_patient",
    )
    date = models.DateTimeField(null=True)
    participant = models.ManyToManyField(
        FamilyMemberHistoryParticipant,
        related_name="family_member_history_participant",
        blank=True,
    )
    name = models.CharField(max_length=255, null=True)
    relationship = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="family_member_history_relationship",
    )
    sex = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="family_member_history_sex",
    )
    born_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        null=True,
        related_name="family_member_history_born_period",
    )
    born_date = models.DateTimeField(null=True)
    born_string = models.CharField(max_length=255, null=True)
    age_age = models.ForeignKey(
        Age,
        on_delete=models.CASCADE,
        null=True,
        related_name="family_member_history_age_age",
    )
    age_range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        null=True,
        related_name="family_member_history_age_range",
    )
    age_string = models.CharField(max_length=255, null=True)
    estimated_age = models.BooleanField(null=True)
    deceased_boolean = models.BooleanField(null=True)
    deceased_age = models.ForeignKey(
        Age,
        on_delete=models.CASCADE,
        null=True,
        related_name="family_member_history_deceased_age",
    )
    deceased_range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        null=True,
        related_name="family_member_history_deceased_range",
    )
    deceased_date = models.DateTimeField(null=True)
    deceased_string = models.CharField(max_length=255, null=True)
    reason = models.ManyToManyField(
        FamilyMemberHistoryReasonCodeableReference,
        related_name="family_member_history_reason",
        blank=True,
    )
    note = models.ManyToManyField(
        Annotation, related_name="family_member_history_note", blank=True
    )
    condition = models.ManyToManyField(
        FamilyMemberHistoryCondition,
        related_name="family_member_history_condition",
        blank=True,
    )
    procedure = models.ManyToManyField(
        FamilyMemberHistoryProcedure,
        related_name="family_member_history_procedure",
        blank=True,
    )
