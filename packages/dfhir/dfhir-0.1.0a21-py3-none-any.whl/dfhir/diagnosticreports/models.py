"""diagnostic report models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    Attachment,
    BaseReference,
    CodeableConcept,
    CodeableReference,
    Identifier,
    Period,
    TimeStampedModel,
)
from dfhir.encounters.models import EncounterReference
from dfhir.medicationrequests.models import MedicationRequest
from dfhir.observations.models import Observation, ObservationReference
from dfhir.patients.models import Patient
from dfhir.practitioners.models import Practitioner
from dfhir.servicerequests.models import ServiceRequest

from .choices import DiagnosticReportStatus


class DiagnosticReportCode(TimeStampedModel):
    """diagnostic report code model."""

    display = models.CharField(max_length=255)
    code = models.CharField(max_length=255, null=True)


class DiagnosticCategory(TimeStampedModel):
    """diagnostic report category model."""

    display = models.CharField(max_length=255)
    description = models.TextField(blank=True)


class ConclusionCode(TimeStampedModel):
    """diagnostic report conclusion code model."""

    display = models.CharField(max_length=255)
    code = models.CharField(max_length=255, null=True)


class DiagnosticReportBasedOnReference(BaseReference):
    """diagnostic report based on model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_based_on_identifier",
    )

    careplan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_based_on_careplan",
    )
    Immunization_recommendation = models.ForeignKey(
        "immunizationrecommendations.ImmunizationRecommendation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_based_on_immunization_recommendation",
    )
    medication_request = models.ForeignKey(
        MedicationRequest,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_based_on_medication_request",
    )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_based_on_nutrition_order",
    )
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_based_on_service_request",
    )


class DiagnosticReportSubjectReference(BaseReference):
    """diagnostic report subject model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_subject_identifier",
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_subject_patient",
    )
    location = models.ForeignKey(
        "locations.Location", on_delete=models.DO_NOTHING, null=True
    )
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.DO_NOTHING, null=True
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_subject_reference_healthcare_service",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_subject_reference_practitioner",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="diagnostic_report_subject_reference_medication",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_subject_reference_group",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_subject_reference_device",
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_subject_reference_substance",
    )
    biologically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_subject_reference_biologically_derived_product",
    )


class DiagnosticReportEffective(TimeStampedModel):
    """diagnostic report effective model."""

    effective_date_time = models.DateTimeField(null=True)
    period = models.ForeignKey(Period, null=True, on_delete=models.DO_NOTHING)


class DiagnosticReportPerformerReference(BaseReference):
    """performer reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="performer_identifier",
    )
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="performer_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="performer_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="performer_organization",
    )
    care_plan = models.ForeignKey(
        "careplans.CarePlan",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="performer_care_plan",
    )


class SupportingInfoReference(BaseReference):
    """supporting info reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supporting_info_reference_identifier",
    )
    imaging_study = models.ForeignKey(
        "imagingstudies.ImagingStudy",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supporting_info_imaging_study",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supporting_info_procedure",
    )
    observation = models.ForeignKey(
        Observation,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supporting_info_observation",
    )
    diagnostic_report = models.ForeignKey(
        "DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supporting_info_diagnostic_report",
    )
    # TODO: citation = models.ForeignKey("Citation", on_delete=models.DO_NOTHING, null=True)
    family_member_history = models.ForeignKey(
        "familymemberhistories.FamilyMemberHistory",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supporting_info_family_member_history",
    )
    allergy_intolerance = models.ForeignKey(
        "allergyintolerances.AllergyIntolerance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supporting_info_allergy_intolerance",
    )
    device_usage = models.ForeignKey(
        "deviceusages.DeviceUsage",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supporting_info_device_usage",
    )


class SupportingInfo(TimeStampedModel):
    """diagnostic report supporting info model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supporting_info_type",
    )
    reference = models.ForeignKey(
        SupportingInfoReference,
        null=True,
        on_delete=models.SET_NULL,
        related_name="supporting_info_reference",
    )


class ConclusionCodeReference(BaseReference):
    """conclusion code reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="conclusion_code_reference_identifier",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="conclusion_code_observation",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="conclusion_code_condition",
    )


class ConclusionCodeCodeableReference(TimeStampedModel):
    """conclusion code codeable reference model."""

    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="conclusion_code_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        ConclusionCodeReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="conclusion_code_codeable_reference_codeable",
    )


class DiagnosticReportMedia(TimeStampedModel):
    """media model."""

    comment = models.TextField(blank=True)
    link = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_report_media_document_reference",
    )


class DiagnosticReport(TimeStampedModel):
    """diagnostic report model."""

    identifier = models.ManyToManyField(
        Identifier,
        blank=True,
        related_name="diagnostic_report_identifier",
    )
    based_on = models.ManyToManyField(
        DiagnosticReportBasedOnReference,
        blank=True,
        related_name="diagnostic_report_based_on",
    )
    status = models.CharField(
        max_length=255, choices=DiagnosticReportStatus.choices, null=True
    )
    category = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="diagnostics_report_category"
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostics_report_code",
    )
    subject = models.ForeignKey(
        DiagnosticReportSubjectReference, on_delete=models.DO_NOTHING, null=True
    )
    encounter = models.ForeignKey(
        EncounterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="diagnostic_encounter",
    )
    effective_date_time = models.DateTimeField(null=True)
    effective_period = models.ForeignKey(
        Period,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="diagnostic_report_effective_period",
    )
    issued = models.DateTimeField(null=True)
    performer = models.ManyToManyField(
        DiagnosticReportPerformerReference,
        blank=True,
        related_name="diagnostic_report_performer",
    )
    results_interpretation = models.ManyToManyField(
        DiagnosticReportPerformerReference,
        blank=True,
        related_name="diagnostic_results_interpretation",
    )

    specimen = models.ManyToManyField(
        "specimens.SpecimenReference",
        blank=True,
        related_name="diagnostic_report_specimen",
    )
    result = models.ManyToManyField(
        ObservationReference, blank=True, related_name="diagnostic_result"
    )
    note = models.ManyToManyField(
        Annotation, blank=True, related_name="diagnostic_report_note"
    )
    # study = models.ManyToManyField(
    #     "genomistudy.GenomicImagingStudyReference",
    #     blank=True,
    #     related_name="diagnostic_report_study",
    # )
    supporting_info = models.ManyToManyField(
        SupportingInfo, blank=True, related_name="diagnostic_report_supporting_info"
    )
    media = models.ManyToManyField(DiagnosticReportMedia, blank=True)
    # TODO: composition = models.ForeignKey(
    #     "Composition",
    #     on_delete=models.DO_NOTHING,
    #     null=True,
    #     related_name="diagnostic_report_composition",
    # )
    conclusion = models.TextField(null=True)
    conclusion_code = models.ManyToManyField(
        ConclusionCodeCodeableReference,
        blank=True,
        related_name="diagnostic_report_conclusion_code",
    )
    recommendation = models.ManyToManyField(CodeableReference, blank=True)
    presented_form = models.ManyToManyField(Attachment, blank=True)
    communication = models.ManyToManyField(
        "communications.CommunicationReference",
        blank=True,
        related_name="diagnostic_report_communication",
    )


class DiagnosticReportDocumentReferenceReference(BaseReference):
    """document reference reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_reference_identifier",
    )
    # TODO: fix!
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_reference_document_reference",
    )
    diagnostic_report = models.ForeignKey(
        DiagnosticReport,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="document_reference_reference_diagnostic_report",
    )
