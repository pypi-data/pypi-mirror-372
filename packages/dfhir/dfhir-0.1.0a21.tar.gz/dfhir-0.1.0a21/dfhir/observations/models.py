"""observation models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    Attachment,
    BaseReference,
    CodeableConcept,
    Identifier,
    Period,
    Quantity,
    Range,
    Ratio,
    Reference,
    TimeStampedModel,
    Timing,
)
from dfhir.bodystructures.models import BodyStructureReference
from dfhir.devices.models import DeviceDeviceMetricReference
from dfhir.encounters.models import EncounterReference
from dfhir.molecularsequences.models import MolecularSequenceReference
from dfhir.observationdefinitions.models import ObservationDefinitionReference
from dfhir.patients.models import Patient, PatientGroupReference
from dfhir.practitioners.models import Practitioner

from .choices import (
    ObservationStatus,
    TriggeredByType,
)


class ObservationReference(BaseReference):
    """observation reference model."""

    identifier = models.ForeignKey(Identifier, on_delete=models.SET_NULL, null=True)
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_reference_observation",
    )


class ObservationBodyStructureReference(BaseReference):
    """observation body structure reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_body_structure_reference_identifier",
    )
    # body_structure = models.ForeignKey(
    #     "BodyStructure",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     related_name="observation_body_structure_reference_body_structure",
    # )


class ObservationBasedOnReference(BaseReference):
    """observation based on reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_based_on_reference_identifier",
    )
    # TODO: care_plan = models.ForeignKey("CarePlan", on_delete=models.SET_NULL, null=True)
    # TODO: device_request = models.ForeignKey("DeviceRequest", on_delete=models.SET_NULL, null=True)
    # TODO: immunization_recommendation = models.ForeignKey("ImmunizationRecommendation", on_delete=models.SET_NULL, null=True)
    medication_request = models.ForeignKey(
        "medicationrequests.MedicationRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_based_on_reference_medication_request",
    )
    nutrition_order = models.ForeignKey(
        "nutritionorders.NutritionOrder",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_based_on_reference_nutrition_order",
    )
    service_request = models.ForeignKey(
        "servicerequests.ServiceRequest",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_based_on_reference_service_request",
    )


class ObservationPartOfReference(BaseReference):
    """observation part of reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_part_of_reference_identifier",
    )
    medication_administration = models.ForeignKey(
        "medicationadministrations.MedicationAdministration",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_part_of_reference_medication_administration",
    )
    medication_dispense = models.ForeignKey(
        "medicationdispenses.MedicationDispense",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_part_of_reference_medication_dispense",
    )
    medication_statement = models.ForeignKey(
        "medicationstatements.MedicationStatement",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_part_of_reference_medication_statement",
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_part_of_reference_procedure",
    )
    immunization = models.ForeignKey(
        "immunizations.Immunization",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_part_of_reference_immunization",
    )
    imaging_study = models.ForeignKey(
        "imagingstudies.ImagingStudy",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_part_of_reference_imaging_study",
    )
    genomic_study = models.ForeignKey(
        "genomicstudies.GenomicStudy",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_part_of_reference_genomic_study",
    )


class ObservationSubjectReference(BaseReference):
    """reference to the subject of the observation."""

    identifier = models.ForeignKey(Identifier, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_subject_reference_group",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_subject_reference_device",
    )
    location = models.ForeignKey(
        "locations.Location", on_delete=models.SET_NULL, null=True
    )
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.SET_NULL, null=True
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_subject_reference_procedure",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner", on_delete=models.SET_NULL, null=True
    )
    medication = models.ForeignKey(
        "medications.Medication", on_delete=models.SET_NULL, null=True
    )
    # TODO: substance = models.ForeignKey(
    #     "substances.Substance", on_delete=models.SET_NULL, null=True
    # )
    biologically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_subject_reference_biologically_derived_product",
    )
    nutrition_product = models.ForeignKey(
        "nutritionproducts.NutritionProduct",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_subject_reference_nutrition_product",
    )


class ObservationTriggeredBy(TimeStampedModel):
    """triggered by model."""

    observation = models.ForeignKey(
        ObservationReference,
        on_delete=models.CASCADE,
        related_name="triggered_by_observation",
    )
    type = models.CharField(max_length=255, null=True, choices=TriggeredByType.choices)
    reason = models.TextField(null=True)


class ObservationHasMemberReference(BaseReference):
    """observation has member reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_has_member_reference_identifier",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_has_member_reference_observation",
    )
    # TODO: questionnaire_response = models.ForeignKey("QuestionnaireResponse", on_delete=models.SET_NULL, null=True)
    molecular_sequence = models.ForeignKey(
        "molecularsequences.MolecularSequence",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_has_member_reference_molecular_sequence",
    )


class ObservationDerivedFromReference(BaseReference):
    """observation derived from reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_derived_from_reference_identifier",
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_derived_from_reference_document_reference",
    )
    imaging_study = models.ForeignKey(
        "imagingstudies.ImagingStudy", on_delete=models.SET_NULL, null=True
    )
    imaging_selection = models.ForeignKey(
        "imagingselections.ImagingSelection", on_delete=models.SET_NULL, null=True
    )
    # TODO: questionnaire_response = models.ForeignKey("QuestionnaireResponse", on_delete=models.SET_NULL, null=True)
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_derived_from_reference_observation",
    )
    molecular_sequence = models.ForeignKey(
        "molecularsequences.MolecularSequence",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_derived_from_reference_molecular_sequence",
    )
    # geometric_study= models.ForeignKey("geometricstudies.GeometricStudy", on_delete=models.SET_NULL, null=True)


class SampledDataIntervalUnitCodes(TimeStampedModel):
    """sampled data interval unit codes model."""

    name = models.CharField(max_length=255, null=True)
    definition = models.TextField(null=True)
    source = models.CharField(max_length=255, null=True)


class SampledData(TimeStampedModel):
    """sampled data model."""

    origin = models.ForeignKey(
        Quantity,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sampled_data_origin",
    )
    interval = models.DecimalField(max_digits=10, null=True, decimal_places=2)
    interval_unit = models.ForeignKey(
        SampledDataIntervalUnitCodes,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sampled_data_interval_unit",
    )

    factor = models.DecimalField(max_digits=10, null=True, decimal_places=2)
    lower_limit = models.DecimalField(max_digits=10, null=True, decimal_places=2)
    upper_limit = models.DecimalField(max_digits=10, null=True, decimal_places=2)
    dimensions = models.IntegerField()
    # TODO: code_map = models.ForeignKey("CodeMap", null=True, on_delete=models.SET_NULL)
    offsets = models.CharField(max_length=255, null=True)
    data = models.TextField(null=True)


class ObservationPerformerReference(BaseReference):
    """observation performer reference model."""

    identifier = models.ForeignKey(Identifier, on_delete=models.SET_NULL, null=True)
    practitioner = models.ForeignKey(
        Practitioner,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_performer_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_performer_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.SET_NULL, null=True
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_performer_reference_care_team",
    )
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.SET_NULL,
        null=True,
    )


class ObservationReferenceRange(TimeStampedModel):
    """reference range model."""

    low = models.ForeignKey(
        Quantity,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reference_range_low",
    )
    high = models.ForeignKey(
        Quantity,
        null=True,
        on_delete=models.SET_NULL,
        related_name="reference_range_high",
    )
    normal_value = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reference_range_normal_value",
    )

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reference_range_type",
    )
    applies_to = models.ManyToManyField(
        CodeableConcept,
        related_name="reference_range_applies_to",
        blank=True,
    )
    age = models.ForeignKey(
        Range, on_delete=models.SET_NULL, null=True, related_name="reference_range_age"
    )
    text = models.TextField(null=True)


class ObservationComponent(TimeStampedModel):
    """observation component model."""

    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        null=True,
        related_name="observation_component_code",
    )
    value_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="observation_component_value",
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.SET_NULL,
        related_name="observation_component_value_codeable_concept",
    )
    value_string = models.CharField(max_length=255, null=True)
    value_boolean = models.BooleanField(null=True)
    value_integer = models.IntegerField(null=True)
    value_range = models.ForeignKey(
        Range,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_component_value_range",
    )
    value_ratio = models.ForeignKey(
        Ratio,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_component_value_ratio",
    )
    value_sampled_data = models.ForeignKey(
        SampledData,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_component_value_sampled_data",
    )
    value_time = models.TimeField(null=True)
    value_date_time = models.DateTimeField(null=True)
    value_period = models.ForeignKey(
        Period,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_component_value_period",
    )
    value_attachment = models.ForeignKey(
        Attachment,
        null=True,
        on_delete=models.SET_NULL,
        related_name="observation_component_value_attachment",
    )
    value_reference = models.ForeignKey(
        MolecularSequenceReference, null=True, on_delete=models.SET_NULL
    )
    data_absent_reason = models.ForeignKey(
        CodeableConcept,
        related_name="observation_component_data_absent_reason",
        null=True,
        on_delete=models.SET_NULL,
    )
    interpretation = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="observation_component_interpretation",
    )
    reference_range = models.ManyToManyField(ObservationReferenceRange, blank=True)


class Observation(TimeStampedModel):
    """observation model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="observation_identifier"
    )
    # TODO: instantiates_canonical = models.CharField(max_length=255, null=True)
    instantiates_reference = models.ForeignKey(
        ObservationDefinitionReference,
        null=True,
        on_delete=models.SET_NULL,
        related_name="observation_instantiates_reference",
    )
    based_on = models.ManyToManyField(
        ObservationBasedOnReference, related_name="observation_based_on", blank=True
    )
    triggered_by = models.ManyToManyField(
        ObservationTriggeredBy, blank=True, related_name="observation_triggered_by"
    )
    part_of = models.ManyToManyField(ObservationPartOfReference, blank=True)

    status = models.CharField(
        max_length=255, null=True, choices=ObservationStatus.choices
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="observation_category", blank=True
    )

    code = models.ForeignKey(CodeableConcept, on_delete=models.DO_NOTHING, null=True)
    subject = models.ForeignKey(
        ObservationSubjectReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="observation_subject",
    )
    focus = models.ManyToManyField(Reference, related_name="observation_focus")
    encounter = models.ForeignKey(
        EncounterReference, on_delete=models.DO_NOTHING, null=True
    )
    effective_date_time = models.DateTimeField(null=True)
    effective_period = models.ForeignKey(
        Period,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_effective_period",
    )
    effective_timing = models.ForeignKey(
        Timing,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_effective_timing",
    )
    effective_instant = models.DateTimeField(null=True)
    issued = models.DateTimeField(null=True)
    performer = models.ManyToManyField(
        ObservationPerformerReference, blank=True, related_name="observation_performer"
    )
    value_quantity = models.ForeignKey(
        Quantity,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="observation_value",
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.SET_NULL,
        related_name="observation_value_codeable_concept",
    )
    value_string = models.CharField(max_length=255, null=True)
    value_boolean = models.BooleanField(null=True)
    value_integer = models.IntegerField(null=True)
    value_range = models.ForeignKey(
        Range,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_value_range",
    )
    value_ratio = models.ForeignKey(
        Ratio,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_value_ratio",
    )
    value_sampled_data = models.ForeignKey(
        SampledData,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_value_sampled_data",
    )
    value_time = models.TimeField(null=True)
    value_date_time = models.DateTimeField(null=True)
    value_period = models.ForeignKey(
        Period,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_value_period",
    )
    value_attachment = models.ForeignKey(
        Attachment,
        null=True,
        on_delete=models.SET_NULL,
        related_name="observation_value_attachment",
    )
    value_reference = models.ForeignKey(
        MolecularSequenceReference, null=True, on_delete=models.SET_NULL
    )
    data_absent_reason = models.ForeignKey(
        CodeableConcept,
        related_name="observation_data_absent_reason",
        null=True,
        on_delete=models.SET_NULL,
    )
    interpretation = models.ManyToManyField(
        CodeableConcept,
        blank=True,
        related_name="observation_interpretation",
    )
    note = models.ManyToManyField(
        Annotation, related_name="observation_note", blank=True
    )
    body_site = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_body_site",
    )
    body_structure = models.ForeignKey(
        BodyStructureReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_body_structure",
    )
    method = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_method",
    )
    specimen = models.ForeignKey(
        PatientGroupReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_specimen",
    )
    device = models.ForeignKey(
        DeviceDeviceMetricReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="observation_device",
    )
    reference_range = models.ManyToManyField(
        ObservationReferenceRange,
        blank=True,
        related_name="observation_reference_range",
    )
    has_member = models.ManyToManyField(
        ObservationHasMemberReference, blank=True, related_name="observation_has_member"
    )
    derived_from = models.ManyToManyField(
        ObservationDerivedFromReference,
        blank=True,
        related_name="observation_derived_from",
    )
    component = models.ManyToManyField(
        ObservationComponent, blank=True, related_name="observation_component"
    )


class ObservationCodeableReference(TimeStampedModel):
    """observation codeable reference model."""

    reference = models.ForeignKey(
        ObservationReference,
        on_delete=models.CASCADE,
        related_name="observation_codeable_reference_reference",
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="observation_codeable_reference_concept",
        null=True,
    )


class DocumentReferenceObservationReference(BaseReference):
    """document reference observation reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="document_reference_observation_reference_identifier",
    )
    observation = models.ForeignKey(
        Observation,
        on_delete=models.SET_NULL,
        null=True,
        related_name="document_reference_observation_reference_observation",
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="document_reference_observation_reference_document_reference",
    )
