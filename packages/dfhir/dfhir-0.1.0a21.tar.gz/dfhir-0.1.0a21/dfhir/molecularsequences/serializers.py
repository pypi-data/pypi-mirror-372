"""molecular sequences serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
)
from dfhir.molecularsequences.models import (
    MolecularSequence,
    MolecularSequenceConcatenated,
    MolecularSequenceConcatenatedSequenceElement,
    MolecularSequenceExtracted,
    MolecularSequenceLiteral,
    MolecularSequenceReference,
    MolecularSequenceRelative,
    MolecularSequenceRelativeEdit,
    MolecularSequenceRepeated,
)


class MolecularSequenceReferenceSerializer(BaseReferenceModelSerializer):
    """molecular reference sreializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = MolecularSequenceReference
        exclude = ["created_at", "updated_at"]


class MolecularSequenceLiteralSerializer(serializers.ModelSerializer):
    """molecular sequence literal serializer."""

    class Meta:
        """Meta options."""

        model = MolecularSequenceLiteral
        exclude = ["created_at", "updated_at"]


class MolecularSequenceRelativeEditSerializer(WritableNestedModelSerializer):
    """molecular sequence relative edit serializer."""

    coordinate_system = CodeableConceptSerializer(many=False, required=False)
    replacement_sequence = MolecularSequenceReferenceSerializer(
        many=False, required=False
    )
    replaced_sequence = MolecularSequenceReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = MolecularSequenceRelativeEdit
        exclude = ["created_at", "updated_at"]


class MolecularSequenceRelativeSerializer(WritableNestedModelSerializer):
    """molecular sequence relative serializer."""

    starting_sequence = MolecularSequenceReferenceSerializer(many=False, required=False)
    relative_edit = MolecularSequenceRelativeEditSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = MolecularSequenceRelative
        exclude = ["created_at", "updated_at"]


class MolecularSequenceExtractedSerializer(WritableNestedModelSerializer):
    """molecular sequence extracted serializer."""

    starting_sequence = MolecularSequenceReferenceSerializer(many=False, required=False)
    coordinated_system = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Metaclass."""

        model = MolecularSequenceExtracted
        exclude = ["created_at", "updated_at"]


class MolecularSequenceRepeatedSerializer(WritableNestedModelSerializer):
    """molecular sequence repeated serializer."""

    sequence_motif = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = MolecularSequenceRepeated
        exclude = ["created_at", "updated_at"]


class MolecularSequenceConcatenatedSequenceElementSerializer(
    WritableNestedModelSerializer
):
    """molecular sequence concatenated sequence element serializer."""

    sequence = MolecularSequenceReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = MolecularSequenceConcatenatedSequenceElement
        exclude = ["created_at", "updated_at"]


class MolecularSequenceConcatenatedSerializer(WritableNestedModelSerializer):
    """molecular sequence concatenated serializer."""

    sequence = MolecularSequenceReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = MolecularSequenceConcatenated
        exclude = ["created_at", "updated_at"]


class MolecularSequenceSerializer(WritableNestedModelSerializer):
    """molecular sequence serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    literal = MolecularSequenceLiteralSerializer(many=False, required=False)
    file = AttachmentSerializer(many=True, required=False)
    relative = MolecularSequenceRelativeSerializer(many=True, required=False)
    extracted = MolecularSequenceExtractedSerializer(many=True, required=False)
    repeated = MolecularSequenceRepeatedSerializer(many=True, required=False)
    concatenated = MolecularSequenceConcatenatedSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = MolecularSequence
        exclude = ["created_at", "updated_at"]
