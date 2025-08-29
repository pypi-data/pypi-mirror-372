"""Models for service requests."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)
from dfhir.patients.models import Patient
from dfhir.practitioners.models import Practitioner

from .choices import (
    ServiceRequestIntent,
    ServiceRequestPriority,
    ServiceRequestStatus,
)


class Parameter(TimeStampedModel):
    """parameter model."""

    display = models.CharField(max_length=255)
    description = models.CharField(max_length=255)


class Reference(TimeStampedModel):
    """reference model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class ServiceRequestCategory(TimeStampedModel):
    """service request category model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class AsNeeded(TimeStampedModel):
    """as needed model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class ProcedureReason(TimeStampedModel):
    """reason model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class BodySite(TimeStampedModel):
    """body site model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class ProcedureCodes(TimeStampedModel):
    """procedure codes model."""

    display = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)


class ServiceRequestBasedOnReference(BaseReference):
    """service request reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_based_on_identifier",
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.SET_NULL,
        related_name="service_request_based_on_care_paln",
        null=True,
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_based_on_service_request",
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_based_on_medication_request",
    )
    # TODO: request_orchestration = models.ForeignKey("RequestOrchestration", on_delete=models.SET_NULL, null=True)
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_based_on_nutrition_order",
    )


class OrderDetailParameterFocusReference(BaseReference):
    """order detail parameter focus reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_identifier",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_device",
    )
    device_definition = models.ForeignKey(
        "devicedefinitions.DeviceDefinition",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_device_definition",
    )
    device_request = models.ForeignKey(
        "devicerequests.DeviceRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_device_request",
    )
    supply_request = models.ForeignKey(
        "supplyrequests.SupplyRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_supply_request",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_medication",
    )
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_medication_request",
    )
    biological_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_reference_biological_derived_product",
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_substance",
    )


class OrderDetailParameterFocusCodeableReference(TimeStampedModel):
    """order detail parameter focus codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        OrderDetailParameterFocusReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_detail_parameter_focus_codeable_reference_reference",
    )


class OrderDetailParameter(TimeStampedModel):
    """order detail parameter."""

    code = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.CASCADE,
        related_name="order_detail_parameter_code",
    )
    value_quantity = models.ForeignKey(
        "base.Quantity",
        null=True,
        on_delete=models.CASCADE,
        related_name="order_detail_parameter_value_quantity",
    )
    value_ratio = models.ForeignKey(
        "base.Ratio",
        null=True,
        on_delete=models.CASCADE,
        related_name="order_detail_parameter_value_ratio",
    )
    value_range = models.ForeignKey(
        "base.Range",
        null=True,
        on_delete=models.CASCADE,
        related_name="order_detail_parameter_value_range",
    )
    value_boolean = models.BooleanField(default=False)
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.CASCADE,
        related_name="order_detail_parameter_value_codeable_concept",
    )
    value_string = models.CharField(max_length=255, null=True)
    value_period = models.ForeignKey(
        "base.Period",
        null=True,
        on_delete=models.CASCADE,
        related_name="order_detail_parameter_value_period",
    )


class ServiceRequestOrderDetail(TimeStampedModel):
    """service request order detail model."""

    parameter_focus = models.ForeignKey(
        OrderDetailParameterFocusCodeableReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_order_detail_parameter_focus",
    )
    parameter = models.ManyToManyField(
        OrderDetailParameter,
        related_name="service_request_order_detail_parameter",
        blank=True,
    )


class ServiceRequestPatientInstruction(TimeStampedModel):
    """patient instruction model."""

    instruction_markdown = models.TextField(null=True)
    instruction_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="patient_instruction_document_reference",
    )


class ServiceRequestSubjectReference(BaseReference):
    """service request subject reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_subject_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_subject_patient",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_subject_group",
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_subject_location",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_subject_device",
    )


class ServiceRequestRequesterReference(BaseReference):
    """service request requester reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_requester_identifier",
    )
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_requester_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_requester_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_requester_organization",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_requester_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_requester_related_person",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_requester_device",
    )


class ServiceRequestPerformerReference(BaseReference):
    """service request performer reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_performer_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_performer_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_performer_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_performer_organization",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_performer_care_team",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_performer_healthcare_service",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_performer_patient",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_performer_device",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_performer_related_person",
    )


class ServiceRequestReasonReference(BaseReference):
    """service request reason reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reason_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reason_condition",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reason_observation",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reason_diagnostic_report",
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reason_document_reference",
    )
    detected_issue = models.ForeignKey(
        "detectedissues.DetectedIssue",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reason_detected_issue",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reason_procedure",
    )


class ServiceRequestReasonCodeableReference(TimeStampedModel):
    """service request codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reason_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        ServiceRequestReasonReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reason_codeable_reference_reference",
    )


class ServiceRequestReference(BaseReference):
    """service request reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reference_identifier",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_reference_service_request",
    )


class ServiceRequest(TimeStampedModel):
    """service request model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="service_request_identifier", blank=True
    )
    # TODO: instantiates_canonical = models.ManyToManyField(
    #     "base.Canonical",
    #     related_name="service_request_instantiates_canonical",
    #     blank=True,
    # )
    instantiates_uri = models.URLField(null=True)
    based_on = models.ManyToManyField(
        ServiceRequestBasedOnReference,
        blank=True,
        related_name="service_request_based_on",
    )
    replaces = models.ManyToManyField(
        ServiceRequestReference,
        blank=True,
        related_name="service_request_replaces",
    )
    requisition = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_requisition",
    )
    status = models.CharField(
        max_length=255,
        choices=ServiceRequestStatus.choices,
        default=ServiceRequestStatus.ACTIVE,
    )
    intent = models.CharField(
        max_length=255,
        choices=ServiceRequestIntent.choices,
        default=ServiceRequestIntent.ORDER,
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="service_request_category", blank=True
    )
    priority = models.CharField(
        max_length=255,
        choices=ServiceRequestPriority.choices,
        default=ServiceRequestPriority.ROUTINE,
    )
    do_not_perform = models.BooleanField(default=False)
    code = models.ForeignKey(
        "activitydefinitions.ActivityDefinitionPlanDefinitionCodeableReference",
        related_name="service_request_code",
        on_delete=models.SET_NULL,
        null=True,
    )
    order_detail = models.ManyToManyField(
        ServiceRequestOrderDetail,
        blank=True,
    )
    quantity_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_quantity_quantity",
    )
    quantity_ratio = models.ForeignKey(
        "base.Ratio",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_quantity_ratio",
    )
    quantity_range = models.ForeignKey(
        "base.Range",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_quantity_range",
    )
    subject = models.ForeignKey(
        ServiceRequestSubjectReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_subject",
    )
    focus = models.ManyToManyField(
        Reference, related_name="service_request_focus", blank=True
    )
    encounter = models.ForeignKey(
        "encounters.EncounterReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_encounter",
    )
    occurrence_date_time = models.DateTimeField(null=True)
    occurrence_period = models.ForeignKey(
        "base.Period",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_occurrence_period",
    )
    occurrence_timing = models.ForeignKey(
        "base.Timing",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_occurrence_timing",
    )
    as_needed = models.BooleanField(default=False)
    as_needed_for = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="service_request_as_needed_for",
    )
    authored_on = models.DateTimeField(null=True)
    requester = models.ForeignKey(
        ServiceRequestRequesterReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_requester",
    )
    additional_recipient = models.ManyToManyField(
        ServiceRequestRequesterReference,
        blank=True,
        related_name="service_request_additional_recipient",
    )
    performer_type = models.ForeignKey(
        CodeableConcept, on_delete=models.SET_NULL, null=True
    )
    performer = models.ManyToManyField(
        ServiceRequestPerformerReference,
        blank=True,
        related_name="service_request_performer",
    )
    location = models.ManyToManyField(
        "locations.LocationCodeableReference",
        blank=True,
        related_name="service_request_location",
    )
    reason = models.ManyToManyField(
        ServiceRequestReasonCodeableReference,
        blank=True,
        related_name="service_request_reason",
    )
    insurance = models.ManyToManyField(
        "coverages.CoverageClaimResponseReference",
        blank=True,
        related_name="service_request_insurance",
    )
    supporting_info = models.ManyToManyField(
        "base.CodeableReference",
        related_name="service_request_supporting_info",
        blank=True,
    )
    specimen = models.ManyToManyField(
        "specimens.SpecimenReference",
        related_name="service_request_specimen",
        blank=True,
    )
    body_site = models.ManyToManyField(
        CodeableConcept, related_name="service_request_body_site", blank=True
    )
    body_structure = models.ForeignKey(
        "bodystructures.BodyStructureReference",
        null=True,
        on_delete=models.SET_NULL,
        related_name="service_request_body_structure",
    )
    note = models.ManyToManyField(
        "base.Annotation", related_name="service_request_note", blank=True
    )
    patient_instruction = models.ManyToManyField(
        ServiceRequestPatientInstruction,
        related_name="service_request_patient_instruction",
        blank=True,
    )
    relevant_history = models.ManyToManyField(
        "provenances.ProvenanceReference",
        related_name="service_request_relevant_history",
        blank=True,
    )


class ServiceRequestPlanDefinitionReference(BaseReference):
    """service request plan definition reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_plan_definition_identifier",
    )
    plan_definition = models.ForeignKey(
        "plandefinitions.PlanDefinition",
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_plan_definition_plan_definition",
    )
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_plan_definition_service_request",
    )


class ServiceRequestPlanDefinitionReferenceCodeableReference(TimeStampedModel):
    """service request plan definition reference codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_plan_definition_reference_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        ServiceRequestPlanDefinitionReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="service_request_plan_definition_reference_codeable_reference_reference",
    )
