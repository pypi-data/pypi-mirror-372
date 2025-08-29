"""flags models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Period,
    TimeStampedModel,
)

from . import choices


class FlagSubjectReference(BaseReference):
    """Flag Subject Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="flag_subject_reference_identifier",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="flag_subject_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="flag_subject_reference_related_person",
        null=True,
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.CASCADE,
        related_name="flag_subject_reference_location",
        null=True,
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="flag_subject_reference_group",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="flag_subject_reference_organization",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="flag_subject_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="flag_subject_reference_practitioner_role",
        null=True,
    )
    # plan_definition = models.ForeignKey("plandefinitions.PlanDefinition", on_delete=models.CASCADE, related_name="flag_subject_reference_plan_definition", null=True)
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.CASCADE,
        related_name="flag_subject_reference_medication",
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.CASCADE,
        related_name="flag_subject_reference_procedure",
        null=True,
    )


class FlagAuthorReference(BaseReference):
    """Flag Author Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="flag_author_reference_identifier",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="flag_author_reference_device",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="flag_author_reference_organization",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="flag_author_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="flag_author_reference_related_person",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="flag_author_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="flag_author_reference_practitioner_role",
        null=True,
    )


class FlagSupportingInfoReference(BaseReference):
    """Flag Supporting Info Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="flag_supporting_info_reference_identifier",
        null=True,
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.CASCADE,
        related_name="flag_supporting_info_reference_observation",
        null=True,
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.CASCADE,
        related_name="flag_supporting_info_reference_condition",
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.CASCADE,
        related_name="flag_supporting_info_reference_procedure",
        null=True,
    )
    allergy_intolerance = models.ForeignKey(
        "allergyintolerances.AllergyIntolerance",
        on_delete=models.CASCADE,
        related_name="flag_supporting_info_reference_allergy_intolerance",
        null=True,
    )
    risk_assessment = models.ForeignKey(
        "riskassessments.RiskAssessment",
        on_delete=models.CASCADE,
        related_name="flag_supporting_info_reference_risk_assessment",
        null=True,
    )


class Flag(TimeStampedModel):
    """Flag model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="flag_identifier",
        blank=True,
    )
    status = models.CharField(
        max_length=255, choices=choices.FlagStatusChoices.choices, null=True
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="flag_category", blank=True
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="flag_code",
        null=True,
    )
    subject = models.ForeignKey(
        FlagSubjectReference,
        on_delete=models.CASCADE,
        related_name="flag_subject",
        null=True,
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="flag_period",
        null=True,
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.CASCADE,
        related_name="flag_encounter",
        null=True,
    )
    author = models.ForeignKey(
        FlagAuthorReference,
        on_delete=models.CASCADE,
        related_name="flag_author",
        null=True,
    )
    supporting_info = models.ManyToManyField(
        FlagSupportingInfoReference,
        related_name="flag_supports",
    )
