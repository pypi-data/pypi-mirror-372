"""medication dispenses models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)
from dfhir.medicationdispenses.choices import MedicationDispenseStatus


class MedicationDispensePerformerActorReference(BaseReference):
    """medication dispense performer actor reference model."""

    identifier = models.ForeignKey(Identifier, on_delete=models.SET_NULL, null=True)
    practitioner = models.ForeignKey(
        "practitioners.Practitioner", on_delete=models.SET_NULL, null=True
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole", on_delete=models.SET_NULL, null=True
    )
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.SET_NULL, null=True
    )
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.SET_NULL, null=True
    )
    device = models.ForeignKey("devices.Device", on_delete=models.SET_NULL, null=True)
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson", on_delete=models.SET_NULL, null=True
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam", on_delete=models.SET_NULL, null=True
    )


class MedicationDispenseReceiverReference(BaseReference):
    """medication dispense receiver reference model."""

    identifier = models.ForeignKey(Identifier, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey(
        "patients.Patient", on_delete=models.SET_NULL, null=True
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner", on_delete=models.SET_NULL, null=True
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson", on_delete=models.SET_NULL, null=True
    )
    location = models.ForeignKey(
        "locations.Location", on_delete=models.SET_NULL, null=True
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole", on_delete=models.SET_NULL, null=True
    )


class MedicationDispensePerformer(TimeStampedModel):
    """medication dispense performer model."""

    function = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_performer_function",
    )
    actor = models.ForeignKey(
        MedicationDispensePerformerActorReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_performer_actor",
    )


class MedicationDispenseSubstitutionResponsiblePartyReference(BaseReference):
    """medication dispense substitution responsibility party."""

    identifier = models.ForeignKey(Identifier, on_delete=models.SET_NULL, null=True)
    practitioner = models.ForeignKey(
        "practitioners.Practitioner", on_delete=models.SET_NULL, null=True
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole", on_delete=models.SET_NULL, null=True
    )
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.SET_NULL, null=True
    )


class MedicationDispenseSubstitution(TimeStampedModel):
    """mediation dispense substitution model."""

    was_substituted = models.BooleanField(default=False)
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_substitution_type",
    )
    reason = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="medication_dispense_substitution_reason",
    )
    responsible_party = models.ManyToManyField(
        MedicationDispenseSubstitutionResponsiblePartyReference,
        blank=True,
        related_name="medication_dispense_substitution_responsible_party",
    )


class MedicationDispense(TimeStampedModel):
    """medication dispense model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="medication_dispense_identifier"
    )

    based_on = models.ManyToManyField("careplans.CarePlanReference", blank=True)

    part_of = models.ManyToManyField(
        "procedures.ProcedureReference",
        blank=True,
        related_name="medication_dispense_part_of",
    )
    status = models.CharField(
        max_length=255, null=True, choices=MedicationDispenseStatus.choices
    )

    not_performed_reason = models.ForeignKey(
        "detectedissues.DetectedIssueCodeableReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_dispense_not_performed_reason",
    )
    status_changed = models.DateTimeField(null=True)
    category = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="medication_dispense_category"
    )

    medication = models.ForeignKey(
        "medications.MedicationCodeableReference",
        on_delete=models.CASCADE,
        null=True,
        related_name="medication_dispense_medication",
    )

    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_subject",
    )

    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_encounter",
    )
    supporting_information = models.ManyToManyField(
        "base.Reference",
        blank=True,
        related_name="medication_dispense_supporting_information",
    )

    performer = models.ManyToManyField(
        MedicationDispensePerformer,
        blank=True,
        related_name="medication_dispense_performer",
    )

    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_location",
    )

    authorizing_prescription = models.ManyToManyField(
        "medicationrequests.MedicationRequestReference",
        blank=True,
        related_name="medication_dispense_authorizing_prescription",
    )

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_type",
    )

    quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_quantity",
    )
    days_supply = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_days_supply",
    )
    recorded = models.DateTimeField(null=True)
    when_prepared = models.DateTimeField(null=True)
    when_handed_over = models.DateTimeField(null=True)
    destination = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_destination",
    )
    receiver = models.ManyToManyField(
        MedicationDispenseReceiverReference,
        blank=True,
        related_name="medication_dispense_receiver",
    )
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="medication_dispense_note"
    )
    rendered_dosage_instructions = models.TextField(null=True)
    # TODO: dosage_instruction = models.ManyToManyField("Dosage", blank=True)
    substitution = models.ForeignKey(
        MedicationDispenseSubstitution,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_dispense_substitution",
    )
    event_history = models.ManyToManyField(
        "provenances.Provenance",
        blank=True,
        related_name="medication_dispense_event_history",
    )
