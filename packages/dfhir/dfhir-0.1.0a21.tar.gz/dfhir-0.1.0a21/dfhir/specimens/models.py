"""specimens models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Duration,
    Identifier,
    SimpleQuantity,
    TimeStampedModel,
)
from dfhir.devices.models import DeviceCodeableReference
from dfhir.procedures.models import ProcedureReference
from dfhir.specimens.choices import SpecimenCombinedChoices, SpecimenStatus
from dfhir.substances.models import SubstanceReference


class SpecimenReference(BaseReference):
    """Specimen reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_reference_identifier",
    )
    specimen = models.ForeignKey(
        "Specimen",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_reference_specimen",
    )


class SpecimenFeature(TimeStampedModel):
    """Specimen feature model."""

    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_feature_type",
    )
    description = models.TextField(null=True)


class SpecimenCollectorReference(BaseReference):
    """Specimen collector reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_collector_reference_identifier",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        related_name="specimen_collector_reference_organization",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        related_name="specimen_collector_reference_practitioner",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        related_name="specimen_collector_reference_practitioner_role",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        related_name="specimen_collector_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        related_name="specimen_collector_reference_related_person",
        null=True,
    )


class SpecimenCollection(TimeStampedModel):
    """Specimen collections model."""

    collector = models.ForeignKey(
        SpecimenCollectorReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_collections_collector",
    )
    collected_date = models.DateTimeField(null=True)
    collected_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        related_name="specimen_collections_collected_period",
        null=True,
    )
    duration = models.ForeignKey(
        Duration,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_collections_duration",
    )
    quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.DO_NOTHING,
        related_name="specimen_collections_method",
        null=True,
    )
    method = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="specimen_collections_method",
        null=True,
    )
    device = models.ForeignKey(
        DeviceCodeableReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_collections_device",
    )
    procedure = models.ForeignKey(
        ProcedureReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_collections_procedure",
    )
    body_site = models.ForeignKey(
        "bodystructures.BodyStructureCodeableReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_collections_body_site",
    )
    fasting_status_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_collections_fasting_status_codeable_concept",
    )
    fasting_status_duration = models.ForeignKey(
        Duration,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_collections_fasting_status_duration",
    )


class SpecimenProcessingPerformerReference(BaseReference):
    """Specimen performer reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_performer_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_performer_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_performer_reference_practitioner_role",
    )

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_performer_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_performer_reference_related_person",
    )


class SpecimenProcessing(TimeStampedModel):
    """Specimen processing model."""

    description = models.TextField(null=True)
    method = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_processing_method",
    )
    performer = models.ForeignKey(
        SpecimenProcessingPerformerReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_processing_performer",
    )
    device = models.ForeignKey(
        "devices.DeviceReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_processing_device",
    )
    additive = models.ManyToManyField(
        SubstanceReference, blank=True, related_name="specimen_processing_additive"
    )
    time_date_time = models.DateTimeField(null=True)
    time_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_processing_time_period",
    )
    time_duration = models.ForeignKey(
        "base.Duration",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_processing_time_duration",
    )


class SpecimenContainer(TimeStampedModel):
    """Specimen container model."""

    device = models.ForeignKey(
        "devices.DeviceReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_container_device",
    )
    specimen_quantity = models.ForeignKey(
        SimpleQuantity,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_container_specimen_quantity",
    )


class SpecimenSubjectReference(BaseReference):
    """Specimen subject reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_subject_reference_identifier",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_subject_reference_patient",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_subject_reference_group",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_subject_reference_device",
    )
    biologically_driven_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_subject_reference_biologically_driven_product",
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="specimen_subject_reference_substance",
    )
    location = models.ForeignKey(
        "locations.Location",
        related_name="specimen_subject_reference_location",
        on_delete=models.DO_NOTHING,
        null=True,
    )


class Specimen(TimeStampedModel):
    """Specimen model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="specimen_identifier", blank=True
    )
    accession_identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        related_name="specimen_accession_identifier",
        null=True,
    )
    status = models.CharField(max_length=255, null=True, choices=SpecimenStatus.choices)
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="specimen_type",
        null=True,
    )
    subject = models.ForeignKey(
        SpecimenSubjectReference,
        on_delete=models.DO_NOTHING,
        related_name="specimen_subject",
    )
    received_time = models.DateTimeField(null=True)
    parent = models.ManyToManyField(
        SpecimenReference, related_name="specimen_parent", blank=True
    )
    request = models.ManyToManyField(
        "servicerequests.ServiceRequestReference",
        related_name="specimen_request",
        blank=True,
    )
    combined = models.CharField(
        max_length=255, null=True, choices=SpecimenCombinedChoices.choices
    )
    role = models.ManyToManyField(
        CodeableConcept, related_name="specimen_role", blank=True
    )
    feature = models.ManyToManyField(
        SpecimenFeature, related_name="specimen_feature", blank=True
    )
    collections = models.ForeignKey(
        SpecimenCollection,
        on_delete=models.DO_NOTHING,
        related_name="specimen_collections",
        null=True,
    )
    processing = models.ManyToManyField(
        SpecimenProcessing, related_name="specimen_processing", blank=True
    )
    container = models.ManyToManyField(
        SpecimenContainer,
        related_name="specimen_container",
        blank=True,
    )
    condition = models.ManyToManyField(
        CodeableConcept, related_name="specimen_condition", blank=True
    )
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="specimen_note"
    )
