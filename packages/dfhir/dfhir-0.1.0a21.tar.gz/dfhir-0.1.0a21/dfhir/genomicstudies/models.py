"""genomic study models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    Reference,
    TimeStampedModel,
)
from dfhir.conditions.models import ConditionObservationCodeableReference
from dfhir.encounters.models import EncounterReference
from dfhir.genomicstudies.choices import GenomicStudyStatusChoices
from dfhir.observations.models import DocumentReferenceObservationReference
from dfhir.practitioners.models import PractitionerPractitionerRoleReference
from dfhir.servicerequests.models import ServiceRequest
from dfhir.specimens.models import SpecimenReference


class GenomicStudyReference(BaseReference):
    """genomic study reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_reference_identifier",
    )
    genomic_study = models.ForeignKey(
        "GenomicStudy",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_reference_genomic_study",
    )


class GenomicStudyAnalysisInput(TimeStampedModel):
    """genomic study analysis input model."""

    file = models.ForeignKey(
        "documentreferences.DocumentReferenceReference",
        on_delete=models.DO_NOTHING,
        related_name="genomic_study_analysis_input_file",
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="genomic_study_analysis_input_type",
        null=True,
    )
    generated_by_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_input_generated_by_identifier",
    )
    generated_by_reference = models.ForeignKey(
        GenomicStudyReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_input_generated_by_reference",
    )


class GenomicStudyAnalysisOutput(TimeStampedModel):
    """genomic study analysis output model."""

    file = models.ForeignKey(
        "documentreferences.DocumentReferenceReference",
        on_delete=models.DO_NOTHING,
        related_name="genomic_study_analysis_output_file",
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="genomic_study_analysis_output_type",
        null=True,
    )


class GenomicStudyAnalysisPerformerActorReference(BaseReference):
    """genomic study analysis performer actor reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_performer_actor_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_performer_actor_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_performer_actor_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_performer_actor_reference_organization",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_performer_actor_reference_device",
    )


class GenomicStudyAnalysisPerformer(TimeStampedModel):
    """genomic study analysis performer model."""

    actor = models.ForeignKey(
        GenomicStudyAnalysisPerformerActorReference,
        on_delete=models.DO_NOTHING,
        related_name="genomic_study_analysis_performer_actor",
        null=True,
    )
    role = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="genomic_study_analysis_performer_role",
        null=True,
    )


class GenomicStudyAnalysisDevice(TimeStampedModel):
    """genomic study analysis device model."""

    device = models.ForeignKey(
        "devices.DeviceReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_device_device",
    )
    function = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_device_function",
    )


class GenomicStudyAnalysisProtocolPerformedReference(BaseReference):
    """procedure task reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="procedure_task_reference_identifier",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.DO_NOTHING,
        related_name="procedure_task_reference_procedure",
        null=True,
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="procedure_task_reference_task",
    )


class GenomicStudyAnalysis(TimeStampedModel):
    """genomic study analysis model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="genomic_study_analysis_identifier"
    )
    method_type = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="genomic_study_analysis_method_type"
    )
    change_type = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="genomic_study_analysis_change_type"
    )
    genomic_build = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_genomic_build",
    )
    # TODO: instantiates_canonical = models.ForeignKey(GenomicStudyReference)
    instantiates_uri = models.URLField(null=True)
    title = models.CharField(max_length=200, null=True)
    focus = models.ManyToManyField(
        Reference, blank=True, related_name="genomic_study_analysis_focus"
    )
    specimen = models.ManyToManyField(
        SpecimenReference, blank=True, related_name="genomic_study_analysis_specimen"
    )
    date = models.DateTimeField(null=True)
    note = models.ManyToManyField(
        Annotation, blank=True, related_name="genomic_study_analysis_note"
    )
    protocol_performed = models.ForeignKey(
        GenomicStudyAnalysisProtocolPerformedReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_analysis_protocol_performed",
    )
    regions_studied = models.ManyToManyField(
        DocumentReferenceObservationReference,
        blank=True,
        related_name="genomic_study_analysis_regions_studied",
    )
    regions_called = models.ManyToManyField(
        DocumentReferenceObservationReference,
        blank=True,
        related_name="genomic_study_analysis_regions_called",
    )
    input = models.ManyToManyField(
        GenomicStudyAnalysisInput,
        blank=True,
        related_name="genomic_study_analysis_input",
    )
    output = models.ManyToManyField(
        GenomicStudyAnalysisOutput,
        blank=True,
        related_name="genomic_study_analysis_output",
    )
    performer = models.ManyToManyField(
        GenomicStudyAnalysisPerformer,
        blank=True,
        related_name="genomic_study_analysis_performer",
    )
    device = models.ManyToManyField(
        GenomicStudyAnalysisDevice,
        blank=True,
        related_name="genomic_study_analysis_device",
    )


class GenomicStudySubjectReference(BaseReference):
    """genomic study subject reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_subject_reference_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_subject_reference_patient",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_subject_reference_group",
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_subject_reference_substance",
    )
    biologically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_subject_reference_biologically_derived_product",
    )
    nutrition_product = models.ForeignKey(
        "nutritionproducts.NutritionProduct",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_subject_reference_nutrition_product",
    )


class GenomicStudyBasedOnReference(BaseReference):
    """genomic study based on reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_based_on_reference_identifier",
    )
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_based_on_reference_service_request",
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_based_on_reference_task",
    )


class GenomicStudy(TimeStampedModel):
    """genomic study model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="genomic_study_identifier"
    )
    status = models.CharField(
        max_length=200, null=True, choices=GenomicStudyStatusChoices.choices
    )
    type = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="genomic_study_type"
    )
    subject = models.ForeignKey(
        GenomicStudySubjectReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_subject",
    )
    encounter = models.ForeignKey(
        EncounterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_encounter",
    )
    start_date = models.DateTimeField(null=True)
    based_on = models.ManyToManyField(
        GenomicStudyBasedOnReference, blank=True, related_name="genomic_study_based_on"
    )
    referrer = models.ForeignKey(
        PractitionerPractitionerRoleReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genomic_study_referrer",
    )
    interpreter = models.ManyToManyField(
        PractitionerPractitionerRoleReference,
        blank=True,
        related_name="genomic_study_interpreter",
    )
    reason = models.ManyToManyField(
        ConditionObservationCodeableReference,
        blank=True,
        related_name="genomic_study_reason",
    )
    # TODO: instantiates_canonical = models.ForeignKey("PlanDefinitionCanonical")
    instantiates_uri = models.URLField(null=True)
    note = models.ManyToManyField(
        Annotation, blank=True, related_name="genomic_study_note"
    )
    description = models.TextField(null=True)
    analysis = models.ManyToManyField(
        GenomicStudyAnalysis, blank=True, related_name="genomic_study_analysis"
    )
