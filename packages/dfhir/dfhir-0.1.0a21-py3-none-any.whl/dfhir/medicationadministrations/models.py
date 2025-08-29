"""medication administrations models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Reference,
    TimeStampedModel,
)
from dfhir.medicationadministrations.choices import MedicationAdministrationStatus


class MedicationAdministrationPartOf(BaseReference):
    """medication administration part of model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        null=True,
        related_name="medication_administration_part_of_identifier",
    )
    medication_administraton = models.ForeignKey(
        "MedicationAdministration",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_part_of_medication_administration",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_part_of_procedure",
    )
    medication_dispense = models.ForeignKey(
        "medicationdispenses.MedicationDispense",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_part_of_medication_dispense",
    )


class MedicationAdministrationPerformerActorReference(BaseReference):
    """medication administration performer actor model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_performer_actor_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_performer_actor_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_performer_actor_practitioner_role",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_performer_actor_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_performer_actor_related_person",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_performer_actor_device",
    )


class MedicationAdministrationPerformerActorCodeableReference(TimeStampedModel):
    """medication administration performer actor codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.SET_NULL,
        related_name="medication_administration_performer_actor_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        MedicationAdministrationPerformerActorReference,
        null=True,
        on_delete=models.SET_NULL,
        related_name="medication_administration_performer_actor_codeable_reference_reference",
    )


class MedicationAdministrationPerformer(TimeStampedModel):
    """medication administration performer model."""

    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_performer_function",
    )
    actor = models.ForeignKey(
        MedicationAdministrationPerformerActorCodeableReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_performer_actor",
    )


class MedicationAdministrationReasonReference(BaseReference):
    """medication administration reason model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_reason_reference_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_reason_reference_condition",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_reason_reference_observation",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_reason_reference_diagnostic_report",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_reason_reference_procedure",
    )


class MedicationAdministrationReasonCodeableReference(TimeStampedModel):
    """medication administration reason codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_reason_codeable_reference_codeable_concept",
    )
    reference = models.ForeignKey(
        MedicationAdministrationReasonReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_reason_codeable_reference_reference",
    )


class MedicationAdministrationDosage(TimeStampedModel):
    """medication administration dosage model."""

    text = models.TextField(null=True)
    site = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_dosage_site",
    )
    route = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_dosage_route",
    )
    method = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_dosage_method",
    )
    dose = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_dosage_dose",
    )
    rate_ratio = models.ForeignKey(
        "base.Ratio",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_dosage_rate_ratio",
    )
    rate_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_dosage_rate_quantity",
    )


class MedicationAdministration(TimeStampedModel):
    """medication administration model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="medication_administration_identifier", blank=True
    )
    based_on = models.ManyToManyField(
        "careplans.CarePlanReference",
        related_name="medication_administration_based_on",
        blank=True,
    )
    part_of = models.ManyToManyField(
        MedicationAdministrationPartOf,
        related_name="medication_administration_part_of",
        blank=True,
    )
    status = models.CharField(
        max_length=200, choices=MedicationAdministrationStatus.choices, null=True
    )
    status_reason = models.ManyToManyField(
        CodeableConcept,
        related_name="medication_administration_status_reason",
        blank=True,
    )
    category = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="medication_administration_category",
    )
    medication = models.ForeignKey(
        "medications.MedicationCodeableReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_medication_codeable_reference",
    )
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_subject",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_encounter",
    )
    supporting_information = models.ManyToManyField(
        Reference,
        related_name="medication_administration_supporting_information",
    )
    occurrence_date_time = models.DateTimeField(null=True)
    occurrence_period = models.ForeignKey(
        "base.Period",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_occurrence_period",
    )
    occurrence_timing = models.ForeignKey(
        "base.Timing",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_occurrence_timing",
    )
    recorded = models.DateTimeField(null=True)
    is_sub_potent = models.BooleanField(null=True)
    sub_potent_reason = models.ManyToManyField(
        CodeableConcept,
        related_name="medication_administration_sub_potent_reason",
        blank=True,
    )
    performer = models.ManyToManyField(
        MedicationAdministrationPerformer,
        related_name="medication_administration_performer",
        blank=True,
    )
    reason = models.ManyToManyField(
        MedicationAdministrationReasonCodeableReference,
        related_name="medication_administration_reason_codeable_reference",
        blank=True,
    )
    request = models.ForeignKey(
        "medicationrequests.MedicationRequestReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_request",
    )
    device = models.ManyToManyField(
        "devices.DeviceCodeableReference",
        related_name="medication_administration_device",
        blank=True,
    )
    note = models.ManyToManyField(
        "base.Annotation",
        related_name="medication_administration_note",
        blank=True,
    )
    dosage = models.ForeignKey(
        MedicationAdministrationDosage,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_administration_dosage",
    )
    event_history = models.ManyToManyField(
        "provenances.ProvenanceReference",
        related_name="medication_administration_event_history",
        blank=True,
    )
