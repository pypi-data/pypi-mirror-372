"""Charge items models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    OrganizationReference,
    TimeStampedModel,
)
from dfhir.chargeitems.choices import ChargeItemStatusChoice


class ChargeItemReference(BaseReference):
    """Charge item reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_reference_identifier",
    )
    charge_item = models.ForeignKey(
        "ChargeItem",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_reference_charge_item",
    )


class ChargeItemPerformerActorReference(BaseReference):
    """charge item performer actor reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_actor_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_actor_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_actor_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_actor_reference_organization",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_actor_reference_healthcare_service",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_actor_reference_care_team",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_actor_reference_patient",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_actor_reference_device",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_actor_reference_related_person",
    )


class ChargeItemPerformer(TimeStampedModel):
    """Charge item performer model."""

    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_function",
    )
    actor = models.ForeignKey(
        ChargeItemPerformerActorReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performer_actor",
    )


class ChargeItemEntererReference(BaseReference):
    """Charge item enterer reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_enterer_reference_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_enterer_reference_condition",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_enterer_reference_diagnostic_report",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_enterer_reference_observation",
    )
    immunization_recommendation = models.ForeignKey(
        "immunizationrecommendations.ImmunizationRecommendation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_enterer_reference_immunization_recommendation",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_enterer_reference_procedure",
    )


class ChargeItemServiceReference(BaseReference):
    """Charge item service reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_identifier",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_diagnostic_report",
    )
    imaging_study = models.ForeignKey(
        "imagingstudies.ImagingStudy",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_imaging_study",
    )
    immunization = models.ForeignKey(
        "immunizations.Immunization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_immunization",
    )
    medication_administration = models.ForeignKey(
        "medicationadministrations.MedicationAdministration",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_medication_administration",
    )
    medication_dispense = models.ForeignKey(
        "medicationdispenses.MedicationDispense",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_medication_dispense",
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_medication_request",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_observation",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_procedure",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_service_request",
    )
    supply_delivery = models.ForeignKey(
        "supplydeliveries.SupplyDelivery",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_reference_supply_delivery",
    )


class ChargeItemServiceCodealbeReference(TimeStampedModel):
    """Charge item service codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        ChargeItemServiceReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_service_codeable_reference_reference",
    )


class ChargeItemProductReference(BaseReference):
    """Charge item product reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_product_reference_identifier",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_product_reference_device",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_product_reference_medication",
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_product_reference_substance",
    )


class ChargeItemProductCodeableReference(TimeStampedModel):
    """Charge item product codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_product_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        ChargeItemProductReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_product_codeable_reference_reference",
    )


class ChargeItemReasonReference(BaseReference):
    """Charge item reason reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_reason_reference_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_reason_reference_condition",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_reason_reference_diagnostic_report",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_reason_reference_observation",
    )
    immunization_recommendation = models.ForeignKey(
        "immunizationrecommendations.ImmunizationRecommendation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_reason_reference_immunization_recommendation",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_reason_reference_procedure",
    )


class ChargeItemReasonCodeableReference(TimeStampedModel):
    """Charge item reason codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_reason_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        ChargeItemReasonReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_reason_codeable_reference_reference",
    )


class ChargeItem(TimeStampedModel):
    """Charge item model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="charge_item_identifier", blank=True
    )
    definition_uri = ArrayField(models.URLField(null=True), null=True)
    # TODO: definition_canonical = models.ForeignKey(ChargeItemDefinitionReference, on_delete=models.DO_NOTHING, null=True, related_name="charge_item_definition_reference_canonical")
    status = models.CharField(
        max_length=255, null=True, choices=ChargeItemStatusChoice.choices
    )
    part_of = models.ManyToManyField(
        ChargeItemReference,
        blank=True,
        related_name="charge_item_reference_part_of",
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_code",
    )
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_subject",
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_encounter",
    )
    occurrence_date_time = models.DateTimeField(null=True)
    occurrence_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_occurrence_period",
    )
    occurrence_timing = models.ForeignKey(
        "base.Timing",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_occurrence_timing",
    )
    performer = models.ManyToManyField(
        ChargeItemPerformer,
        blank=True,
        related_name="charge_item_performer",
    )
    performing_organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_performing_organization",
    )
    requesting_organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_requesting_organization",
    )
    cost_center = models.ForeignKey(
        OrganizationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_cost_center",
    )
    quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_quantity",
    )
    body_site = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="charge_item_body_site",
    )
    unit_price_component = models.ForeignKey(
        "base.MonetaryComponent",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_unit_price_component",
    )

    total_price_component = models.ForeignKey(
        "base.MonetaryComponent",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_total_price_component",
    )

    override_reason = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_override_reason",
    )
    enterer = models.ForeignKey(
        ChargeItemEntererReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="charge_item_enterer",
    )
    entered_date = models.DateTimeField(null=True)
    reason = models.ManyToManyField(
        ChargeItemReasonCodeableReference, blank=True, related_name="charge_item_reason"
    )
    service = models.ManyToManyField(
        ChargeItemServiceCodealbeReference,
        blank=True,
        related_name="charge_item_service",
    )
    product = models.ManyToManyField(
        ChargeItemProductCodeableReference,
        blank=True,
        related_name="charge_item_product",
    )
    account = models.ManyToManyField(
        "accounts.AccountReference",
        blank=True,
        related_name="charge_item_account",
    )
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="charge_item_note"
    )
    supporting_information = models.ManyToManyField(
        "base.Reference", blank=True, related_name="charge_item_supporting_information"
    )
