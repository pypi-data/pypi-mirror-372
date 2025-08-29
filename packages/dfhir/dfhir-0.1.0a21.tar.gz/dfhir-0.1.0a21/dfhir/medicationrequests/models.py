"""medication requests models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    OrganizationReference,
    Period,
    Quantity,
    Reference,
    TimeStampedModel,
)
from dfhir.base.models import Quantity as Duration
from dfhir.devices.models import DeviceCodeableReference
from dfhir.encounters.models import EncounterReference
from dfhir.medicationrequests.choices import (
    MedicationIntent,
    MedicationRequestPriority,
    MedicationRequestStatus,
)
from dfhir.medications.models import MedicationCodeableReference
from dfhir.organizations.models import Organization
from dfhir.patients.models import Patient
from dfhir.patients.models import PatientGroupReference as SubjectReference
from dfhir.practitioners.models import (
    Practitioner,
    PractitionerPractitionerRoleReference,
)
from dfhir.provenances.models import ProvenanceReference


class MedicationRequestCategory(TimeStampedModel):
    """medication request category model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class MedicationRequestMedicationCode(TimeStampedModel):
    """medication request medication codes."""

    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)


class MedicationRequestReferenceType(TimeStampedModel):
    """medication request reference type."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class MedicationRequestReason(TimeStampedModel):
    """medication requests reasons."""

    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)


class AdditionalIllustration(TimeStampedModel):
    """additional illustration model."""

    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)


class ReferenceAsNeededFor(TimeStampedModel):
    """as needed for model."""

    code = models.CharField(max_length=255, null=False)
    display = models.CharField(max_length=255, null=True)


class DosageSite(TimeStampedModel):
    """dosage site model."""

    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)


class DosageRoute(TimeStampedModel):
    """dosage route model."""

    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)


class DosageMethod(TimeStampedModel):
    """dosage method model."""

    code = models.CharField(max_length=255, null=True)
    display = models.CharField(max_length=255, null=True)


class MedicationRequestBasedOnReference(BaseReference):
    """medication request based on reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_based_on_identifier",
    )
    medication_request = models.ForeignKey(
        "MedicationRequest",
        on_delete=models.DO_NOTHING,
        related_name="medication_request_based_on_reference",
        null=True,
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_based_on_care_plan",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_based_on_service_request",
    )
    immunization_recommendation = models.ForeignKey(
        "immunizationrecommendations.ImmunizationRecommendation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_based_on_immunization_recommendation",
    )
    # TODO: request_orchestration = models.ForeignKey(
    #     "RequestOrchestration", on_delete=models.DO_NOTHING, null=True
    # )


class MedicationRequestReference(BaseReference):
    """medication reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_reference_identifier",
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.DO_NOTHING,
        related_name="medication_request_reference",
        null=True,
    )


class medicationRequestInformationSourceReference(BaseReference):
    """medication request information source reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_information_source_reference_identifier",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_information_source_reference_patient",
    )
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_information_source_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_information_source_reference_practitioner_role",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson", on_delete=models.DO_NOTHING, null=True
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_information_source_reference_organization",
    )


class MedicationRequestRequesterReference(BaseReference):
    """medication request requester reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_requester_reference_identifier",
    )
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_requester_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_requester_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_requester_reference_organization",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_requester_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_requester_reference_related_person",
    )
    device = models.ForeignKey("devices.Device", on_delete=models.DO_NOTHING, null=True)


class MedicationRequestPerformerReference(BaseReference):
    """medication request performer reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_performer_reference_identifier",
    )
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_performer_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        null=True,
        on_delete=models.SET_NULL,
        related_name="medication_request_performer_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_performer_reference_organization",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_performer_reference_patient",
    )
    device_definition = models.ForeignKey(
        "devicedefinitions.DeviceDefinition",
        null=True,
        on_delete=models.SET_NULL,
        related_name="medication_request_performer_reference_device_definition",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson", null=True, on_delete=models.SET_NULL
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam", null=True, on_delete=models.SET_NULL
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        null=True,
        on_delete=models.SET_NULL,
        related_name="medication_request_performer_reference_healthcare_service",
    )


class MedicationRequestReasonReference(BaseReference):
    """medication request  reason reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_codeble_reason_reference_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition", null=True, on_delete=models.SET_NULL
    )
    observation = models.ForeignKey(
        "observations.Observation",
        null=True,
        on_delete=models.SET_NULL,
        related_name="medication_request_reason_reference_observation",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        null=True,
        on_delete=models.SET_NULL,
        related_name="medication_request_reason_reference_diagnostic_report",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        null=True,
        on_delete=models.SET_NULL,
        related_name="medication_request_reason_reference_procedure",
    )


class MedicatonRequestReasonCodealbleReference(TimeStampedModel):
    """medication request reason codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_reason_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        MedicationRequestReasonReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_reason_codeable_reference_reference",
    )


class DispenseRequestInitialFill(TimeStampedModel):
    """dispense request initial fill model."""

    quantity = models.ForeignKey(
        Quantity,
        null=True,
        on_delete=models.SET_NULL,
        related_name="dispense_request_initial_fill_quantity",
    )
    duration = models.ForeignKey(
        Duration,
        null=True,
        on_delete=models.SET_NULL,
        related_name="dispense_request_initial_fill_duration",
    )


class DispenseRequest(TimeStampedModel):
    """dispense requester model."""

    initial_fill = models.ForeignKey(
        DispenseRequestInitialFill,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dispense_request_initial_fill",
    )
    dispense_interval = models.ForeignKey(
        Duration,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dispense_request_dispense_interval",
    )
    validity_period = models.ForeignKey(
        Period,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dispense_request_validity_period",
    )
    number_of_repeats_allowed = models.IntegerField(null=True)
    quantity = models.ForeignKey(
        Quantity,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dispense_request_quantity",
    )
    expected_supply_duration = models.ForeignKey(
        Duration, on_delete=models.SET_NULL, null=True
    )
    dispenser = models.ForeignKey(
        OrganizationReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dispense_request_dispenser",
    )
    dispense_instruction = models.ManyToManyField(
        Annotation, blank=True, related_name="dispense_request_instruction"
    )
    dose_administration_aid = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="dispense_request_dose_administration_aid",
    )


class MedicationRequestSubstitution(TimeStampedModel):
    """medication request substitution model."""

    allowed_boolean = models.BooleanField(default=True)
    allowed_codeable_concept = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.SET_NULL,
        related_name="medication_request_substitution_allowed_codeable_concept",
    )
    reason = models.ForeignKey(
        CodeableConcept,
        related_name="medication_request_substitution_reason",
        null=True,
        on_delete=models.SET_NULL,
    )


class MedicationRequestInsuranceReference(BaseReference):
    """medication request insurance reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_insurance_reference_identifier",
    )
    coverage = models.ForeignKey(
        "coverages.Coverage",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_insurance_reference_coverage",
    )
    claim_response = models.ForeignKey(
        "claimresponses.ClaimResponse",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_insurance_reference_claim_response",
    )


class MedicationRequestProvinanceReference(BaseReference):
    """medication request insurance reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_provinance_reference_identifier",
    )
    provenance = models.ForeignKey(
        "provenances.Provenance",
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_provinance_reference_provenance",
    )


class MedicationRequest(TimeStampedModel):
    """medication request model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="medication_request_identifier"
    )
    based_on = models.ManyToManyField(
        MedicationRequestBasedOnReference,
        blank=True,
        related_name="medication_request_based_on",
    )
    prior_prescription = models.ForeignKey(
        MedicationRequestReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_prior_prescription",
    )
    group_identifier = models.ForeignKey(
        Identifier,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="medication_request_group_identifier",
    )
    status = models.CharField(
        max_length=255,
        null=True,
        choices=MedicationRequestStatus.choices,
    )
    status_reason = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="medication_request_status_reason",
    )
    status_changed = models.DateTimeField(null=True)
    intent = models.CharField(
        max_length=255, null=True, choices=MedicationIntent.choices
    )
    category = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="medication_request_category"
    )
    priority = models.CharField(
        max_length=255,
        null=True,
        choices=MedicationRequestPriority.choices,
    )
    do_not_perform = models.BooleanField(default=False)
    medication = models.ForeignKey(
        MedicationCodeableReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_mepatientdication",
    )
    subject = models.ForeignKey(
        SubjectReference,
        on_delete=models.DO_NOTHING,
        related_name="medication_request_subject",
        null=True,
    )
    information_source = models.ManyToManyField(
        medicationRequestInformationSourceReference,
        blank=True,
        related_name="medication_request_information_source",
    )
    encounter = models.ForeignKey(
        EncounterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_encounter",
    )
    supporting_information = models.ManyToManyField(
        Reference, blank=True, related_name="medication_request_supporting_information"
    )
    authored_on = models.DateTimeField(null=True)
    requester = models.ForeignKey(
        MedicationRequestRequesterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_requester",
    )
    reported = models.BooleanField(default=True)
    performer_type = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="medication_request_performer_type",
    )
    performer = models.ForeignKey(
        MedicationRequestPerformerReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_performer",
    )
    device = models.ManyToManyField(
        DeviceCodeableReference,
        blank=True,
        related_name="medication_request_device",
    )
    recorder = models.ForeignKey(
        PractitionerPractitionerRoleReference,
        on_delete=models.DO_NOTHING,
        related_name="medication_request_recorder",
        null=True,
    )
    reason = models.ManyToManyField(
        MedicatonRequestReasonCodealbleReference,
        blank=True,
        related_name="medication_request_reason",
    )
    course_of_therapy_type = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="medication_request_course_of_therapy_type",
    )
    insurance = models.ManyToManyField(
        MedicationRequestInsuranceReference,
        blank=True,
        related_name="medication_request_insurance",
    )
    note = models.ManyToManyField(
        Annotation, blank=True, related_name="medication_request_note"
    )
    rendered_dosage_instruction = models.TextField(null=True)
    effective_dose_period = models.ForeignKey(
        Period,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="medication_request_effective_dose_period",
    )
    # TODO: dosage_instruction = models.ManyToManyField("dosages.Dosage", blank=True)
    dispense_request = models.ForeignKey(
        DispenseRequest,
        on_delete=models.DO_NOTHING,
        related_name="medication_request_dispense_request",
        null=True,
    )
    substitution = models.ForeignKey(
        MedicationRequestSubstitution,
        on_delete=models.SET_NULL,
        null=True,
        related_name="medication_request_substitution",
    )
    event_history = models.ManyToManyField(
        ProvenanceReference,
        blank=True,
        related_name="medication_request_event_history",
    )
