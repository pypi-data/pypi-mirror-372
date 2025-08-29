"""immunization app models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Reference,
    TimeStampedModel,
)
from dfhir.immunizations.choices import ImmunizationStatusChoices


class ImmunizationBasedOnReference(BaseReference):
    """Immunization based on reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_based_on_references",
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_based_on_references",
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_based_on_references",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_based_on_references",
    )
    immunization_recommendation = models.ForeignKey(
        "immunizationrecommendations.ImmunizationRecommendation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_based_on_references",
    )


class ImmunizationInformationSourceRefrence(BaseReference):
    """immunization information source reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_information_source_references",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_information_source_references",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_information_source_references",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_information_source_references",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_information_source_references",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_information_source_references",
    )


class ImmunizationPerformerActorReference(BaseReference):
    """immunization performer actor reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_performer_actor_references",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_performer_actor_references",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_performer_actor_references",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_performer_actor_references",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_performer_actor_references",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_performer_actor_references",
    )


class ImmunizationPerformer(TimeStampedModel):
    """immunization performer model."""

    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_performers",
    )
    actor = models.ForeignKey(
        ImmunizationPerformerActorReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_performers",
    )


class ImmunizationReasonReference(BaseReference):
    """immunization reason reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_reason_references_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_reason_references_condition",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_reason_references_observation",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_reason_references_diagnostic_report",
    )


class ImmunizationReasonCodeableReference(TimeStampedModel):
    """immunization reason codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_reason_codeable_references_identifier",
    )
    reference = models.ForeignKey(
        ImmunizationReasonReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_reason_codeable_references_reference",
    )


class ImmunizationProgramEligibility(TimeStampedModel):
    """immunization program eligibility model."""

    program = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_program_eligibility_program",
    )
    program_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_program_eligibility_program_status",
    )


class ImmunizationProtocolApplied(TimeStampedModel):
    """immunization protocol applied model."""

    series = models.CharField(max_length=255, null=True)
    authority = models.ForeignKey(
        "base.OrganizationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_protocol_applied_authority",
    )
    target_disease = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="immunization_protocol_applied_usage_disease",
    )
    dose_number = models.CharField(max_length=255, null=True)
    series_dose = models.CharField(max_length=255, null=True)


class ImmunizationReaction(TimeStampedModel):
    """immunization reaction model."""

    date = models.DateTimeField(null=True)
    manifestation = models.ForeignKey(
        "observations.ObservationCodeableReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_reaction_detail",
    )
    reported = models.BooleanField(default=False)


class Immunization(TimeStampedModel):
    """immunization model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="immunization_identifier"
    )
    based_on = models.ManyToManyField(
        ImmunizationBasedOnReference, blank=True, related_name="immunization_based_on"
    )
    status = models.CharField(
        max_length=255, null=True, choices=ImmunizationStatusChoices.choices
    )
    status_reason = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_status_reason",
    )
    vaccine_code = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_vaccine_code",
    )
    administered_product = models.ForeignKey(
        "medications.MedicationCodeableReference",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_administered_product",
    )
    manufacturer = models.ForeignKey(
        "organizations.OrganizationCodeableReference",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_manufacturer",
    )
    lot_number = models.CharField(max_length=255, null=True)
    expiration_date = models.DateField(null=True)
    patient = models.ForeignKey(
        "patients.PatientReference",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_patient",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_encounter",
    )
    supporting_infortmation = models.ManyToManyField(
        Reference, blank=True, related_name="immunization_supporting_infortmation"
    )
    occurrence_date_time = models.DateTimeField(null=True)
    occurrence_string = models.CharField(max_length=255, null=True)
    primary_source = models.BooleanField(default=False)
    information_source = models.ForeignKey(
        ImmunizationInformationSourceRefrence,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_information_source",
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_location",
    )
    site = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_site",
    )
    route = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_route",
    )
    dose_quantity = models.ForeignKey(
        "base.SimpleQuantity",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_dose_quantity",
    )
    performer = models.ManyToManyField(
        ImmunizationPerformer, blank=True, related_name="immunization_performer"
    )
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="immunization_note"
    )
    reason = models.ManyToManyField(
        ImmunizationReasonCodeableReference,
        blank=True,
        related_name="immunization_reason",
    )
    is_subpotent = models.BooleanField(default=False)
    subpotent_reason = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="immunization_subpotent_reason"
    )
    program_eligibility = models.ManyToManyField(
        ImmunizationProgramEligibility,
        blank=True,
        related_name="immunization_program_eligibility",
    )
    funding_source = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="immunization_funding_source",
    )
    reaction = models.ManyToManyField(
        ImmunizationReaction, blank=True, related_name="immunization_reaction"
    )
    protocol_applied = models.ManyToManyField(
        ImmunizationProtocolApplied,
        blank=True,
        related_name="immunization_protocol_applied",
    )


class ImmunizationReference(BaseReference):
    """immunization reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_reference_identifier",
    )
    immunization = models.ForeignKey(
        Immunization,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="immunization_reference_immunization",
    )
