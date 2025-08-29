"""molecular sequences models."""

from django.db import models

from dfhir.base.models import (
    Attachment,
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)
from dfhir.molecularsequences.choices import MolecularSequenceTypeChoices


class MolecularSequenceReference(BaseReference):
    """Molecular sequence reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        related_name="molecular_sequence_reference_identifier",
        null=True,
    )
    molecular_sequence = models.ForeignKey(
        "MolecularSequence",
        on_delete=models.SET_NULL,
        related_name="molecular_sequence_reference_molecular_sequence",
        null=True,
    )


class MolecularSequenceLiteral(TimeStampedModel):
    """Molecular sequence literal model."""

    sequence_value = models.CharField(max_length=255, null=True)


class MolecularSequenceRelativeEdit(TimeStampedModel):
    """Molecular sequence relative edit model."""

    edit_order = models.IntegerField()
    coordinate_system = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="molecular_sequence_relative_edit_coordinate_system",
    )
    start = models.IntegerField(null=True)
    end = models.IntegerField(null=True)
    replacement_sequence = models.ForeignKey(
        MolecularSequenceReference,
        on_delete=models.DO_NOTHING,
        related_name="molecular_sequence_relative_edit_replacement_sequence",
    )
    replaced_sequence = models.ForeignKey(
        MolecularSequenceReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="molecular_sequence_relative_edit_replaced_sequence",
    )


class MolecularSequenceRelative(TimeStampedModel):
    """Molecular sequence relative model."""

    starting_sequence = models.ForeignKey(
        MolecularSequenceReference,
        on_delete=models.SET_NULL,
        related_name="molecular_sequence_relative_starting_sequence",
        null=True,
    )
    edit = models.ManyToManyField(
        MolecularSequenceRelativeEdit,
        blank=True,
        related_name="molecular_sequence_relative_edit",
    )


class MolecularSequenceExtracted(TimeStampedModel):
    """Molecular sequence extracted model."""

    starting_sequence = models.ForeignKey(
        MolecularSequenceReference,
        on_delete=models.SET_NULL,
        related_name="molecular_sequence_extracted_starting_sequence",
        null=True,
    )
    start = models.IntegerField(null=True)
    end = models.IntegerField(null=True)
    coordinated_system = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="molecular_sequence_extracted_coordinated_system",
    )
    reverse_complement = models.BooleanField(default=False)


class MolecularSequenceRepeated(TimeStampedModel):
    """Molecular sequence repeated model."""

    sequence_motif = models.ForeignKey(
        MolecularSequenceReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="molecular_sequence_repeated_sequence_motif",
    )
    copy_count = models.IntegerField(null=True)


class MolecularSequenceConcatenatedSequenceElement(TimeStampedModel):
    """Molecular sequence concatenated sequence element model."""

    sequence = models.ForeignKey(
        MolecularSequenceReference,
        null=True,
        related_name="molecular_sequence_concatenated_sequence",
        on_delete=models.SET_NULL,
    )
    ordinate_index = models.IntegerField(null=True)


class MolecularSequenceConcatenated(TimeStampedModel):
    """Molecular sequence concatenated model."""

    sequence_element = models.ManyToManyField(
        MolecularSequenceConcatenatedSequenceElement,
        blank=True,
        related_name="molecular_sequence_concatenated_sequence_element",
    )


class MolecularSequence(TimeStampedModel):
    """Molecular sequence model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="molecular_sequence_identifier"
    )
    type = models.CharField(
        max_length=255, null=True, choices=MolecularSequenceTypeChoices.choices
    )
    literal = models.ManyToManyField(
        MolecularSequenceLiteral, blank=True, related_name="molecular_sequence_literal"
    )
    file = models.ManyToManyField(
        Attachment, blank=True, related_name="molecular_sequence_file"
    )
    relative = models.ManyToManyField(
        MolecularSequenceRelative,
        blank=True,
        related_name="molecular_sequence_relative",
    )
    extracted = models.ManyToManyField(
        MolecularSequenceExtracted,
        blank=True,
        related_name="molecular_sequence_extracted",
    )
    repeated = models.ManyToManyField(
        MolecularSequenceRepeated,
        blank=True,
        related_name="molecular_sequence_repeated",
    )
    concatenated = models.ManyToManyField(
        MolecularSequenceConcatenated,
        blank=True,
        related_name="molecular_sequence_concatenated",
    )
