"""molecular definitions models."""

from django.contrib.postgres.fields import ArrayField
from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)

# Create your models here.


class MolecularDefinitionReference(BaseReference):
    """Molecular definition reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_reference_identifier",
    )
    molecular_definition = models.ForeignKey(
        "MolecularDefinition",
        on_delete=models.DO_NOTHING,
        related_name="molecular_definition_reference_molecular_definition",
        null=True,
    )


class MolecularDefinitionCoordinateIntervalCoordinateSystem(TimeStampedModel):
    """molecular definition coordinate interval coordinate system model."""

    system = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_coordinate_interval_coordinate_system_system",
    )
    origin = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_coordinate_interval_coordinate_system_origin",
    )
    normalization_method = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_coordinate_interval_coordinate_system_method",
    )

    start_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_coordinate_interval_coordinate_system_start_quantity",
    )
    start_range = models.ForeignKey(
        "base.Range",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_coordinate_interval_coordinate_system_start_range",
    )
    end_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_coordinate_interval_coordinate_system_end_quantity",
    )
    end_range = models.ForeignKey(
        "base.Range",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_coordinate_interval_coordinate_system_end_range",
    )


class MolecularDefinitionCoordinateInterval(TimeStampedModel):
    """molecular definition relative edit coordinate interval model."""

    coordinate_system = models.ForeignKey(
        MolecularDefinitionCoordinateIntervalCoordinateSystem,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_relative_edit_coordinate_system",
    )


class MolecularDefinitionSequenceLocation(TimeStampedModel):
    """Sequence location model."""

    sequence_context = models.ForeignKey(
        MolecularDefinitionReference,
        on_delete=models.DO_NOTHING,
        blank=True,
        related_name="sequence_location_sequence_context",
    )
    coordinated_interval = models.ForeignKey(
        MolecularDefinitionCoordinateInterval,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="sequence_location_coordinated_internal",
    )
    strand = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="sequence_location_strand",
    )


class MolecularSequenceGenomeAssembly(TimeStampedModel):
    """Genome assembly model."""

    organism = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genome_assembly_organism",
    )
    build = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genome_assembly_build",
    )
    accession = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="genome_assembly_accession",
    )
    description_markdown = models.TextField(null=True)
    description_string = models.CharField(max_length=255, null=True)


class MolecularDefinitionCytobandIntervalStartEndCytoband(TimeStampedModel):
    """Cytoband interval start cytoband model."""

    arm_code = models.CharField(max_length=255, null=True)
    arm_string = models.CharField(max_length=255, null=True)
    region_code = models.CharField(max_length=255, null=True)
    region_string = models.CharField(max_length=255, null=True)
    band_code = models.CharField(max_length=255, null=True)
    band_string = models.CharField(max_length=255, null=True)
    sub_band_code = models.CharField(max_length=255, null=True)
    sub_band_string = models.CharField(max_length=255, null=True)


class MolecularDefinitionCytobandInterval(TimeStampedModel):
    """Cytoband interval model."""

    chromosome = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="cytoband_interval_chromosome",
    )
    start_cytoband = models.ForeignKey(
        MolecularDefinitionCytobandIntervalStartEndCytoband,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="cytoband_interval_start_cytoband",
    )
    end_cytoband = models.ForeignKey(
        MolecularDefinitionCytobandIntervalStartEndCytoband,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="cytoband_interval_end_cytoband",
    )


class MolecularDefinitionCytobandLocation(TimeStampedModel):
    """Cytoband location model."""

    genome_assembly = models.ForeignKey(
        MolecularSequenceGenomeAssembly,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="cytoband_location_genome_assembly",
    )
    cytoband_interval = models.ForeignKey(
        MolecularDefinitionCytobandInterval,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="cytoband_location_cytoband_interval",
    )


class MolecularDefinitionLocation(TimeStampedModel):
    """Molecular definition location model."""

    sequence_location = models.ForeignKey(
        MolecularDefinitionSequenceLocation,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_sequence_location",
    )
    cytoband_location = models.ForeignKey(
        MolecularDefinitionCytobandLocation,
        on_delete=models.DO_NOTHING,
        related_name="molecular_definition_cytoband_location",
        null=True,
    )
    featured_location = ArrayField(
        models.CharField(max_length=255, null=True), null=True
    )


class MolecularDefinitionRepresentationLiteral(TimeStampedModel):
    """representation literal model."""

    encoding = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_literal_encoding",
    )
    value = models.CharField(max_length=255, null=True)


class MolecularDefinitionRepresentationExtracted(TimeStampedModel):
    """representation extracted model."""

    starting_molecule = models.ForeignKey(
        MolecularDefinitionReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_extract_string_molecule",
    )
    coordinate_interval = models.ForeignKey(
        MolecularDefinitionCoordinateInterval,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_extracted_coordinate_interval",
    )
    reverse_complement = models.BooleanField(default=False)


class MolecularDefinitionRepresentationRepeated(TimeStampedModel):
    """representation repeated model."""

    sequence_motif = models.ForeignKey(
        MolecularDefinitionReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_extract_sequence_motif",
    )
    copy_count = models.IntegerField(null=True)


class MolecularDefinitionRepresentationConcatenatedSequenceElement(TimeStampedModel):
    """representation concatenated sequence element model."""

    sequence = models.ForeignKey(
        MolecularDefinitionReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_concatenated_sequence_element_sequence",
    )
    ordinal_index = models.IntegerField(null=True)


class MolecularDefinitionRepresentationConcatenated(TimeStampedModel):
    """representation concatenated model."""

    sequence_element = models.ManyToManyField(
        MolecularDefinitionRepresentationConcatenatedSequenceElement,
        blank=True,
        related_name="representation_concatenated",
    )


class MolecularDefinitionRepresentationRelativeEdit(TimeStampedModel):
    """representation relative edit model."""

    edit_order = models.IntegerField(null=True)
    coordinate_interval = models.ForeignKey(
        MolecularDefinitionCoordinateInterval,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_representation_relative_edit_coordinate_interval",
    )
    coordinate_system = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="molecular_representation_coordinate_system",
        null=True,
    )
    replacement_molecule = models.ForeignKey(
        MolecularDefinitionReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_representation_relative_edit_replacement_molecule",
    )
    replaced_molecule = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        related_name="molecular_representation_edit_replaced_molecule",
        null=True,
    )


class MolecularDefinitionRepresentationRelative(TimeStampedModel):
    """representation relative model."""

    starting_molecule = models.ForeignKey(
        MolecularDefinitionReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_starting_molecule",
    )
    edit = models.ManyToManyField(
        MolecularDefinitionRepresentationRelativeEdit,
        related_name="representation_edit_relative",
        blank=True,
    )


class MolecularDefinitionRepresentation(TimeStampedModel):
    """representation model."""

    focus = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_focus",
    )
    code = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="representation_code"
    )
    literal = models.ForeignKey(
        MolecularDefinitionRepresentationLiteral,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_literal",
    )
    resolvable = models.ForeignKey(
        "documentreferences.DocumentReferenceReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_resolvable",
    )
    extracted = models.ForeignKey(
        MolecularDefinitionRepresentationExtracted,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_extracted",
    )
    repeated = models.ForeignKey(
        MolecularDefinitionRepresentationRepeated,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_repeat",
    )
    concatenated = models.ForeignKey(
        MolecularDefinitionRepresentationConcatenated,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_concatenated",
    )
    relative = models.ForeignKey(
        MolecularDefinitionRepresentationRelative,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="representation_relative",
    )


class MolecularDefinition(TimeStampedModel):
    """molecular definition model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="molecular_definition_identifier"
    )
    description = models.TextField(null=True)
    molecular_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="molecular_definition_molecular_type",
    )
    type = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="molecular_definition_type"
    )
    topology = models.ManyToManyField(
        CodeableConcept, blank=True, related_name="molecular_definition_topology"
    )
    member_state = models.ManyToManyField(
        MolecularDefinitionReference,
        blank=True,
        related_name="molecular_definition_member_state",
    )
    location = models.ManyToManyField(
        MolecularDefinitionLocation,
        blank=True,
        related_name="molecular_definition_location",
    )
    representation = models.ManyToManyField(
        MolecularDefinitionRepresentation,
        blank=True,
        related_name="molecular_definition_representation",
    )
