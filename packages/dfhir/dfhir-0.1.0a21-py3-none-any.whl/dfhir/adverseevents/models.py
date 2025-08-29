"""Adverse events models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    Period,
    TimeStampedModel,
)

from . import choices


class AdverseEventSubjectReference(BaseReference):
    """Adverse event subject reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="adverse_event_subject_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="adverse_event_subject_reference_patient",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="adverse_event_subject_reference_group",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="adverse_event_subject_reference_practitioner",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="adverse_event_subject_reference_related_person",
        null=True,
    )


class AdverseEventRecorderReference(BaseReference):
    """Adverse event recorder reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="adverse_event_recorder_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="adverse_event_recorder_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="adverse_event_recorder_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="adverse_event_recorder_reference_practitioner_role",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="adverse_event_recorder_reference_related_person",
        null=True,
    )


class AdverseEventContributingFactorReference(BaseReference):
    """Adverse event contributing factor reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_identifier",
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_condition",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_observation",
        null=True,
    )
    allergy_intolerance = models.ForeignKey(
        "allergyintolerances.AllergyIntolerance",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_allergy_intolerance",
        null=True,
    )
    family_member_history = models.ForeignKey(
        "familymemberhistories.FamilyMemberHistory",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_family_member_history",
        null=True,
    )
    immunization = models.ForeignKey(
        "immunizations.Immunization",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_immunization",
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_procedure",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_device",
        null=True,
    )
    device_usage = models.ForeignKey(
        "deviceusages.DeviceUsage",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_device_usage",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_document_reference",
        null=True,
    )
    medication_administration = models.ForeignKey(
        "medicationadministrations.MedicationAdministration",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_medication_administration",
        null=True,
    )
    medication_statement = models.ForeignKey(
        "medicationstatements.MedicationStatement",
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_reference_medication_statement",
        null=True,
    )


class AdverseEventContributingFactorCodeableReference(TimeStampedModel):
    """Adverse event contributing factor codeable reference model."""

    reference = models.ForeignKey(
        AdverseEventContributingFactorReference,
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_codeable_reference_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="adverse_event_contributing_factor_codeable_reference_concept",
        null=True,
    )


class AdverseEventPreventiveActionReference(BaseReference):
    """Adverse event preventive action reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="adverse_event_preventive_action_reference_identifier",
        null=True,
    )
    immunization = models.ForeignKey(
        "immunizations.Immunization",
        on_delete=models.CASCADE,
        related_name="adverse_event_preventive_action_reference_immunization",
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.CASCADE,
        related_name="adverse_event_preventive_action_reference_procedure",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.CASCADE,
        related_name="adverse_event_preventive_action_reference_document_reference",
        null=True,
    )
    medication_administration = models.ForeignKey(
        "medicationadministrations.MedicationAdministration",
        on_delete=models.CASCADE,
        related_name="adverse_event_preventive_action_reference_medication_administration",
        null=True,
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.CASCADE,
        related_name="adverse_event_preventive_action_reference_medication_request",
        null=True,
    )


class AdverseEventPreventiveActionCodeableReference(TimeStampedModel):
    """Adverse event preventive action codeable reference model."""

    reference = models.ForeignKey(
        AdverseEventPreventiveActionReference,
        on_delete=models.CASCADE,
        related_name="adverse_event_preventive_action_codeable_reference_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="adverse_event_preventive_action_codeable_reference_concept",
        null=True,
    )


class AdverseEventMitigatingActionReference(BaseReference):
    """Adverse event mitigating action reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="adverse_event_mitigating_action_reference_identifier",
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.CASCADE,
        related_name="adverse_event_mitigating_action_reference_procedure",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.CASCADE,
        related_name="adverse_event_mitigating_action_reference_document_reference",
        null=True,
    )
    medication_administration = models.ForeignKey(
        "medicationadministrations.MedicationAdministration",
        on_delete=models.CASCADE,
        related_name="adverse_event_mitigating_action_reference_medication_administration",
        null=True,
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.CASCADE,
        related_name="adverse_event_mitigating_action_reference_medication_request",
        null=True,
    )


class AdverseEventMitigatingActionCodeableReference(TimeStampedModel):
    """Adverse event mitigating action codeable reference model."""

    reference = models.ForeignKey(
        AdverseEventMitigatingActionReference,
        on_delete=models.CASCADE,
        related_name="adverse_event_mitigating_action_codeable_reference_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="adverse_event_mitigating_action_codeable_reference_concept",
        null=True,
    )


class AdverseEventSupportingInfoReference(BaseReference):
    """Adverse event supporting info reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_reference_identifier",
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_reference_condition",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_reference_observation",
        null=True,
    )
    allergy_intolerance = models.ForeignKey(
        "allergyintolerances.AllergyIntolerance",
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_reference_allergy_intolerance",
        null=True,
    )
    family_member_history = models.ForeignKey(
        "familymemberhistories.FamilyMemberHistory",
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_reference_family_member_history",
        null=True,
    )
    immunization = models.ForeignKey(
        "immunizations.Immunization",
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_reference_immunization",
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_reference_procedure",
        null=True,
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_reference_document_reference",
        null=True,
    )
    medication_administration = models.ForeignKey(
        "medicationadministrations.MedicationAdministration",
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_reference_medication_administration",
        null=True,
    )
    medication_statement = models.ForeignKey(
        "medicationstatements.MedicationStatement",
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_reference_medication_statement",
        null=True,
    )
    # questionnaire_response = models.ForeignKey(
    #     "questionnaireresponses.QuestionnaireResponse",
    #     on_delete=models.CASCADE,
    #     related_name="adverse_event_supporting_info_reference_questionnaire_response",
    #     null=True,
    # )


class AdverseEventSupportingInfoCodeableReference(TimeStampedModel):
    """Adverse Event supporting info codeable reference."""

    reference = models.ForeignKey(
        "AdverseEventSupportingInfoReference",
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_codeable_reference_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="adverse_event_supporting_info_codeable_reference_concept",
        null=True,
    )


class AdverseEventSuspectEntityInstanceReference(BaseReference):
    """Adverse event suspect entity instance reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_reference_identifier",
        null=True,
    )
    immunization = models.ForeignKey(
        "immunizations.Immunization",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_reference_immunization",
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_reference_procedure",
        null=True,
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_reference_substance",
        null=True,
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_reference_medication",
        null=True,
    )
    medication_administration = models.ForeignKey(
        "medicationadministrations.MedicationAdministration",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_reference_medication_administration",
        null=True,
    )
    medication_statement = models.ForeignKey(
        "medicationstatements.MedicationStatement",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_reference_medication_statement",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_reference_device",
        null=True,
    )
    biollogically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_reference_biologically_derived_product",
        null=True,
    )
    # research_study = models.ForeignKey(
    #     "researchstudies.ResearchStudy",
    #     on_delete=models.CASCADE,
    #     related_name="adverse_event_suspect_entity_instance_reference_research_study",
    #     null=True,
    # )


class AdverseEventSuspectEntityInstanceCodeableReference(TimeStampedModel):
    """Adverse event suspect entity instance codeable reference model."""

    reference = models.ForeignKey(
        AdverseEventSuspectEntityInstanceReference,
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_codeable_reference_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_instance_codeable_reference_concept",
        null=True,
    )


class AdverseEventSuspectEntityAuthorReference(BaseReference):
    """Adverse event suspect entity author reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_author_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_author_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_author_reference_practitioner_role",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_author_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_author_reference_related_person",
        null=True,
    )


class AdverseEventSuspectEntityCausality(TimeStampedModel):
    """Adverse event suspect entity causality model."""

    assessment_method = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_causality_assessment",
        null=True,
    )
    entity_relatedness = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_causality_entity_relatedness",
        null=True,
    )
    author = models.ForeignKey(
        AdverseEventSuspectEntityAuthorReference,
        on_delete=models.CASCADE,
        related_name="adverse_event_suspect_entity_causality_author",
        null=True,
    )


class AdverseEventSuspectEntity(TimeStampedModel):
    """Adverse event suspect entity model."""

    instance = models.ForeignKey(
        AdverseEventSuspectEntityInstanceCodeableReference,
        on_delete=models.DO_NOTHING,
        related_name="adverse_event_suspect_entity_instance",
        null=True,
    )
    causality = models.ForeignKey(
        AdverseEventSuspectEntityCausality,
        on_delete=models.DO_NOTHING,
        related_name="adverse_event_suspect_entity_causality",
        null=True,
    )


class AdverseEventParticipantActorReference(BaseReference):
    """Adverse event participant actor reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="adverse_event_participant_actor_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="adverse_event_participant_actor_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="adverse_event_participant_actor_reference_practitioner_role",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="adverse_event_participant_actor_reference_organization",
        null=True,
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.CASCADE,
        related_name="adverse_event_participant_actor_reference_care_team",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="adverse_event_participant_actor_reference_patient",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="adverse_event_participant_actor_reference_device",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="adverse_event_participant_actor_reference_related_person",
        null=True,
    )


class AdverseEventParticipant(TimeStampedModel):
    """Adverse event participant model."""

    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="adverse_event_participant_function",
        null=True,
    )
    actor = models.ForeignKey(
        AdverseEventParticipantActorReference,
        on_delete=models.DO_NOTHING,
        related_name="adverse_event_participant_actor",
        null=True,
    )


class AdverseEvent(TimeStampedModel):
    """Adverse event model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="adverse_event_identifier",
        blank=True,
    )
    status = models.CharField(
        max_length=255, choices=choices.AdverseEventStatusChoices.choices
    )
    actuality = models.CharField(
        max_length=255, choices=choices.AdverseEventActualityChoices.choices
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="adverse_event_category", blank=True
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="adverse_event_code",
        null=True,
    )
    subject = models.ForeignKey(
        AdverseEventSubjectReference,
        on_delete=models.DO_NOTHING,
        related_name="adverse_event_subject",
        null=True,
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        related_name="adverse_event_encounter",
        null=True,
    )
    cause_date_time = models.DateTimeField(null=True)
    cause_period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="adverse_event_cause_period",
    )
    effect_date_time = models.DateTimeField(null=True)
    effect_period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="adverse_event_effect_period",
    )
    detected = models.DateTimeField(null=True)
    recorded_date = models.DateTimeField(null=True)
    resulting_effect = models.ManyToManyField(
        "conditions.ConditionObservationCodeableReference",
        related_name="adverse_event_resulting_effect",
        blank=True,
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        related_name="adverse_event_location",
        null=True,
    )
    seriousness = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="adverse_event_seriousness",
        null=True,
    )
    outcome = models.ManyToManyField(
        CodeableConcept, related_name="adverse_event_outcome", blank=True
    )
    recorder = models.ForeignKey(
        AdverseEventRecorderReference,
        on_delete=models.DO_NOTHING,
        related_name="adverse_event_recorder",
        null=True,
    )
    participant = models.ManyToManyField(
        AdverseEventParticipant,
        related_name="adverse_event_participant",
        blank=True,
    )
    # study = models.ManyToManyField(
    #     "researchstudies.ResearchStudy",
    #     related_name="adverse_event_study",
    #     blank=True,
    # )
    expected_in_research_study = models.BooleanField(default=False)
    suspect_entity = models.ManyToManyField(
        AdverseEventSuspectEntity,
        related_name="adverse_event_suspect_entity",
        blank=True,
    )
    contributing_factor = models.ManyToManyField(
        AdverseEventContributingFactorCodeableReference,
        related_name="adverse_event_contributing_factor",
        blank=True,
    )
    preventive_action = models.ManyToManyField(
        AdverseEventPreventiveActionCodeableReference,
        related_name="adverse_event_preventive_action",
        blank=True,
    )
    mitigating_action = models.ManyToManyField(
        AdverseEventMitigatingActionCodeableReference,
        related_name="adverse_event_mitigating_action",
        blank=True,
    )
    supporting_info = models.ManyToManyField(
        AdverseEventSupportingInfoCodeableReference,
        related_name="adverse_event_supporting_info",
        blank=True,
    )
    note = models.ManyToManyField(
        Annotation, related_name="adverse_event_note", blank=True
    )
