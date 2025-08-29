"""medication statements models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Reference,
    TimeStampedModel,
)
from dfhir.medicationstatements.choices import MedicationStatementStatusChoices


class MedicationStatementPartOfReference(BaseReference):
    """medication statement part of reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_part_of_reference_identifier",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_part_of_reference_procedure",
    )
    medication_statement = models.ForeignKey(
        "MedicationStatement",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_part_of_reference_medication_statement",
    )


class MedicationStatementInformationSourceReference(BaseReference):
    """medication statement information source reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_information_source_reference_identifier",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_information_source_reference_device",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="medication_statement_information_source_reference_patient",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="medication_statement_information_source_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="medication_statement_information_source_reference_practitioner_role",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="medication_statement_information_source_reference_related_person",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="medication_statement_information_source_reference_organization",
        null=True,
    )


class MedicationStatementReasonReference(BaseReference):
    """medication statement reason reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_reason_reference_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_reason_reference_condition",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_reason_reference_observation",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_reason_reference_diagnostic_report",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_reason_reference_procedure",
    )


class MedicationStatementAdherence(TimeStampedModel):
    """medication statement adherence model."""

    code = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_adherence_code",
    )
    reason = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_adherence_reason",
    )


class MedicationStatement(TimeStampedModel):
    """medication statement model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="medication_statement_identifier"
    )
    part_of = models.ManyToManyField(
        MedicationStatementPartOfReference,
        blank=True,
        related_name="medication_statement_part_of",
    )
    status = models.CharField(
        max_length=255, null=True, choices=MedicationStatementStatusChoices.choices
    )
    category = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="medication_statement_category"
    )
    medication = models.ForeignKey(
        "medications.MedicationCodeableReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_medication",
    )
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_subject",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_encounter",
    )
    effective_date_time = models.DateTimeField(null=True)
    effective_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_statement_effective_period",
    )
    effective_timing = models.ForeignKey(
        "base.Timing",
        on_delete=models.ForeignKey,
        null=True,
        related_name="medication_statement_effective_timing",
    )
    date_asserted = models.DateTimeField(null=True)
    information_source = models.ManyToManyField(
        MedicationStatementInformationSourceReference,
        blank=True,
        related_name="medication_statement_information_source",
    )
    derived_from = models.ManyToManyField(
        Reference, blank=True, related_name="medication_statement_derived_from"
    )
    reason = models.ManyToManyField(
        MedicationStatementReasonReference,
        blank=True,
        related_name="medication_statement_reason",
    )
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="medication_statement_note"
    )
    related_clinical_information = models.TextField(null=True)
    # TODO: dosage = models.ManyToManyField(
    #     "Dosage", blank=True, related_name="medication_statement_dosage"
    # )
    adherence = models.ForeignKey(
        MedicationStatementAdherence,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="medication_statement_adherence",
    )
