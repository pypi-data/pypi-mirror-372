"""Detected issues models."""

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
from dfhir.practitioners.models import PractitionerPractitionerRoleReference

from . import choices


class DetectedIssueSubjectReference(BaseReference):
    """Detected issue subject reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_patient",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_group",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_device",
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_location",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_organization",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_procedure",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_practitioner",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_medication",
    )
    biologically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_biologically_derived_product",
    )
    nutrition_product = models.ForeignKey(
        "nutritionproducts.NutritionProduct",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_nutrition_product",
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_subject_reference_substance",
    )


class DetectedIssueAuthorReference(BaseReference):
    """Detected issue author reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_author_reference_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_author_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_author_reference_related_person",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_author_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_author_reference_practitioner_role",
    )

    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_author_reference_device",
    )


class DetectedIssueEvidence(TimeStampedModel):
    """Detected issue evidence model."""

    code = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="detected_issue_evidence_code",
    )
    detail = models.ManyToManyField(
        Reference, blank=True, related_name="detected_issue_evidence_detail"
    )


class DetectedIssueMitigation(TimeStampedModel):
    """Detected issue mitigation model."""

    action = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_mitigation_action",
    )
    date = models.DateTimeField(null=True)
    author = models.ForeignKey(
        PractitionerPractitionerRoleReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_mitigation_author",
    )
    note = models.ManyToManyField(
        Annotation, blank=True, related_name="detected_issue_mitigation_note"
    )


class DetectedIssue(TimeStampedModel):
    """Detected issue model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="detected_issue_identifier"
    )
    status = models.CharField(
        max_length=255, null=True, choices=choices.DetectedIssueStatusChoices.choices
    )
    category = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="detected_issue_category",
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_code",
    )
    severity = models.CharField(
        max_length=255, null=True, choices=choices.DetectedIssueSeverityChoices.choices
    )
    subject = models.ForeignKey(
        DetectedIssueSubjectReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_patient",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_encounter",
    )
    identified_date_time = models.DateTimeField(null=True)
    identified_period = models.ForeignKey(Period, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(
        DetectedIssueAuthorReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="detected_issue_author",
    )
    implicated = models.ManyToManyField(
        Reference,
        blank=True,
        related_name="detected_issue_implicated",
    )
    evidence = models.ManyToManyField(
        DetectedIssueEvidence, blank=True, related_name="detected_issue_evidence"
    )
    detail = models.TextField(null=True)
    reference = models.URLField(null=True)
    mitigation = models.ManyToManyField(
        DetectedIssueMitigation, blank=True, related_name="detected_issue_mitigation"
    )


class DetectedIssueReference(BaseReference):
    """detected issue reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="detected_issue_reference_identifier",
    )
    detected_issue = models.ForeignKey(
        DetectedIssue,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="detected_issue_reference_detected_issue",
    )


class DetectedIssueCodeableReference(TimeStampedModel):
    """detected issue codeable reference."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="detected_issue_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        DetectedIssueReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="detected_issue_codeable_reference_reference",
    )
