"""AllergyIntolerances models."""

from django.contrib.postgres.fields import ArrayField
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


class AllergyIntoleranceRecorderReference(BaseReference):
    """Allergy Intolerance Recorder Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_recorder_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_recorder_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_recorder_reference_practitioner_role",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_recorder_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_recorder_reference_related_person",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_recorder_reference_organization",
        null=True,
    )


class AllergyIntoleranceAsserterReference(BaseReference):
    """Allergy Intolerance Asserter Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_asserter_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_asserter_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_asserter_reference_practitioner_role",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_asserter_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_asserter_reference_related_person",
        null=True,
    )


class AllergyIntoleranceReaction(TimeStampedModel):
    """Allergy Intolerance Reaction model."""

    substance = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_reaction_substance",
        null=True,
    )
    manifestation = models.ManyToManyField(
        "observations.ObservationCodeableReference",
        related_name="allergy_intolerance_reaction_manifestation",
        blank=True,
    )
    description = models.TextField(null=True)
    onset = models.DateTimeField(null=True)
    severity = models.CharField(
        max_length=255,
        choices=choices.AllergyIntoleranceSeverity.choices,
        null=True,
    )
    exposure_route = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_reaction_exposure_route",
        null=True,
    )
    note = models.ManyToManyField(
        Annotation, related_name="allergy_intolerance_reaction_note", blank=True
    )


class AllergyIntolerance(TimeStampedModel):
    """Allergy Intolerance model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="allergy_intolerance_identifier",
        blank=True,
    )
    clinical_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_clinical_status",
        null=True,
    )
    verification_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_verification_status",
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_type",
        null=True,
    )
    category = ArrayField(
        models.CharField(
            max_length=255,
            choices=choices.AllergyIntoleranceCategory.choices,
        ),
        null=True,
    )
    criticality = models.CharField(
        max_length=255,
        choices=choices.AllergyIntoleranceCriticality.choices,
        null=True,
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_code",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_patient",
        null=True,
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_encounter",
        null=True,
    )
    onset_date_time = models.DateTimeField(null=True)
    onset_age = models.ForeignKey(
        Age,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_onset_age",
        null=True,
    )
    onset_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_onset_period",
        null=True,
    )
    onset_range = models.ForeignKey(
        Range,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_onset_range",
        null=True,
    )
    onset_string = models.CharField(max_length=255, null=True)
    recorded_date = models.DateTimeField(null=True)
    recorder = models.ForeignKey(
        AllergyIntoleranceRecorderReference,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_recorder",
        null=True,
    )
    asserter = models.ForeignKey(
        AllergyIntoleranceAsserterReference,
        on_delete=models.CASCADE,
        related_name="allergy_intolerance_asserter",
        null=True,
    )
    last_reaction_occurrence = models.DateTimeField(null=True)
    note = models.ManyToManyField(
        Annotation, related_name="allergy_intolerance_note", blank=True
    )
    reaction = models.ManyToManyField(
        AllergyIntoleranceReaction,
        related_name="allergy_intolerance_reaction",
        blank=True,
    )


class AllergyIntoleranceReference(BaseReference):
    """allergy intolerance reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="allergy_intolerance_reference_identifier",
    )
    allergy_intolerance = models.ForeignKey(
        AllergyIntolerance,
        on_delete=models.SET_NULL,
        null=True,
        related_name="allergy_intolerance_reference_allergy_intolerance",
    )
