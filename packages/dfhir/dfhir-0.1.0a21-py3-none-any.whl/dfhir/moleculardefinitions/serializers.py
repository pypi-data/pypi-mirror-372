"""molecular definition serializers."""

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    QuantitySerializer,
    RangeSerializer,
)
from dfhir.documentreferences.serializers import DocumentReferenceReferenceSerializer
from dfhir.moleculardefinitions.models import (
    MolecularDefinition,
    MolecularDefinitionCoordinateInterval,
    MolecularDefinitionCoordinateIntervalCoordinateSystem,
    MolecularDefinitionCytobandInterval,
    MolecularDefinitionCytobandIntervalStartEndCytoband,
    MolecularDefinitionCytobandLocation,
    MolecularDefinitionLocation,
    MolecularDefinitionReference,
    MolecularDefinitionRepresentation,
    MolecularDefinitionRepresentationConcatenated,
    MolecularDefinitionRepresentationConcatenatedSequenceElement,
    MolecularDefinitionRepresentationExtracted,
    MolecularDefinitionRepresentationLiteral,
    MolecularDefinitionRepresentationRelative,
    MolecularDefinitionRepresentationRelativeEdit,
    MolecularDefinitionRepresentationRepeated,
    MolecularDefinitionSequenceLocation,
    MolecularSequenceGenomeAssembly,
)


class MolecularDefinitionReferenceSerializer(BaseReferenceModelSerializer):
    """molecular definition reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = MolecularDefinitionReference
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionCoordinateIntervalCoordinateSystemSerializer(
    WritableNestedModelSerializer
):
    """molecular definition coordinate interval coordinate system serializer."""

    system = CodeableConceptSerializer(required=False)
    origin = CodeableConceptSerializer(required=False)
    normalization_method = CodeableConceptSerializer(required=False)
    start_quantity = QuantitySerializer(required=False)
    start_range = RangeSerializer(required=False)
    end_quantity = QuantitySerializer(required=False)
    end_range = RangeSerializer(required=False)

    class Meta:
        """Meta options."""

        model = MolecularDefinitionCoordinateIntervalCoordinateSystem
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionCoordinateIntervalSerializer(WritableNestedModelSerializer):
    """molecular definition coordinate interval serializer."""

    coordinate_system = MolecularDefinitionCoordinateIntervalCoordinateSystemSerializer(
        required=False
    )

    class Meta:
        """Meta options."""

        model = MolecularDefinitionCoordinateInterval
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionRepresentationLiteralSerializer(WritableNestedModelSerializer):
    """molecular definition representation literal serializer."""

    encoding = CodeableConceptSerializer(required=False)

    class Meta:
        """meta options."""

        model = MolecularDefinitionRepresentationLiteral
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionRepresentationExtractedSerializer(
    WritableNestedModelSerializer
):
    """molecular definition representation extracted serializer."""

    string_molecule = MolecularDefinitionReferenceSerializer(required=False)
    coordinate_system = CodeableConceptSerializer(required=False)

    class Meta:
        """meta options."""

        model = MolecularDefinitionRepresentationExtracted
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionRepresentationRepeatedSerializer(
    WritableNestedModelSerializer
):
    """molecular definition representation repeated serializer."""

    sequence_motif = MolecularDefinitionReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = MolecularDefinitionRepresentationRepeated
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionRepresentationConcatenatedSequenceElementSerializer(
    WritableNestedModelSerializer
):
    """molecular definition representation concatenated sequence element serializer."""

    sequence = MolecularDefinitionReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = MolecularDefinitionRepresentationConcatenatedSequenceElement
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionRepresentationConcatenatedSerializer(
    WritableNestedModelSerializer
):
    """molecular definition representation concatenated sequence element serializer."""

    sequence_element = (
        MolecularDefinitionRepresentationConcatenatedSequenceElementSerializer(
            required=False, many=True
        )
    )

    class Meta:
        """meta options."""

        model = MolecularDefinitionRepresentationConcatenated
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionRepresentationRelativeEditSerializer(
    WritableNestedModelSerializer
):
    """molecular definition representation relative edit serializer."""

    coordinate_system = CodeableConceptSerializer(required=False)
    replacement_molecule = MolecularDefinitionReferenceSerializer(required=False)
    replaced_molecule = CodeableConceptSerializer(required=False)

    class Meta:
        """meta options."""

        model = MolecularDefinitionRepresentationRelativeEdit
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionRepresentationRelativeSerializer(
    WritableNestedModelSerializer
):
    """molecular definition representation relative serializer."""

    starting_molecule = MolecularDefinitionReferenceSerializer(required=False)
    edit = MolecularDefinitionRepresentationRelativeEditSerializer(
        required=False, many=True
    )

    class Meta:
        """meta options."""

        model = MolecularDefinitionRepresentationRelative
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionRepresentationSerializer(WritableNestedModelSerializer):
    """molecular definition representation serializer."""

    focus = CodeableConceptSerializer(required=False)
    code = CodeableConceptSerializer(required=False)
    literal = MolecularDefinitionRepresentationLiteralSerializer(required=False)
    resolvable = DocumentReferenceReferenceSerializer(required=False)
    extracted = MolecularDefinitionRepresentationExtractedSerializer(required=False)
    repeated = MolecularDefinitionRepresentationRepeatedSerializer(required=False)
    concatenated = MolecularDefinitionRepresentationConcatenatedSerializer(
        required=False
    )
    relative = MolecularDefinitionRepresentationRelativeSerializer(required=False)

    class Meta:
        """meta options."""

        model = MolecularDefinitionRepresentation
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionSequenceLocationSerializer(WritableNestedModelSerializer):
    """molecular definition sequence location serializer."""

    sequence_context = MolecularDefinitionReferenceSerializer(required=False)
    coordinated_interval = MolecularDefinitionCoordinateIntervalSerializer(
        required=False
    )
    strand = CodeableConceptSerializer(required=False)

    class Meta:
        """meta options."""

        model = MolecularDefinitionSequenceLocation
        exclude = ["created_at", "updated_at"]


class MolecularSequenceGenomeAssemblySerializer(WritableNestedModelSerializer):
    """molecular sequence genome assembly serializer."""

    organism = CodeableConceptSerializer(required=False)
    build = CodeableConceptSerializer(required=False)
    accession = CodeableConceptSerializer(required=False)

    class Meta:
        """meta options."""

        model = MolecularSequenceGenomeAssembly
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionCytobandIntervalStartEndCytobandSerializer(
    serializers.ModelSerializer
):
    """molecular definition cytoband interval start/end serializer."""

    class Meta:
        """meta options."""

        model = MolecularDefinitionCytobandIntervalStartEndCytoband
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionCytobandIntervalSerializer(WritableNestedModelSerializer):
    """molecular definition cytoband interval serializer."""

    chromosome = CodeableConceptSerializer(required=False)
    start_cytoband = MolecularDefinitionCytobandIntervalStartEndCytobandSerializer(
        required=False
    )
    end_cytoband = MolecularDefinitionCytobandIntervalStartEndCytobandSerializer(
        required=False
    )

    class Meta:
        """meta options."""

        model = MolecularDefinitionCytobandInterval
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionCytobandLocationSerializer(WritableNestedModelSerializer):
    """molecular definition cytoband location serializer."""

    genome_assembly = MolecularSequenceGenomeAssemblySerializer(required=False)
    cytoband_interval = MolecularDefinitionCytobandIntervalSerializer(required=False)

    class Meta:
        """meta options."""

        model = MolecularDefinitionCytobandLocation
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionLocationSerializer(WritableNestedModelSerializer):
    """molecular definition location serializer."""

    sequence_location = MolecularDefinitionSequenceLocationSerializer(required=False)
    cytoband_location = MolecularDefinitionCytobandLocationSerializer(required=False)

    class Meta:
        """meta options."""

        model = MolecularDefinitionLocation
        exclude = ["created_at", "updated_at"]


class MolecularDefinitionSerializer(WritableNestedModelSerializer):
    """Serializer for MolecularDefinition model."""

    identifier = IdentifierSerializer(required=False, many=True)
    molecule_type = CodeableConceptSerializer(required=False)
    type = CodeableConceptSerializer(required=False, many=True)
    topology = CodeableConceptSerializer(required=False, many=True)
    location = MolecularDefinitionLocationSerializer(many=True, required=False)
    member_state = MolecularDefinitionReferenceSerializer(required=False, many=True)
    representation = MolecularDefinitionRepresentationSerializer(
        required=False, many=True
    )

    class Meta:
        """meta options."""

        model = MolecularDefinition
        exclude = ["created_at", "updated_at"]
