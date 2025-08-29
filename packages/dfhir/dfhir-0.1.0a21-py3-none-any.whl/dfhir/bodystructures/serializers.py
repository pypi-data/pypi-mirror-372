"""body structures serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    QuantitySerializer,
)
from dfhir.bodystructures.models import (
    BodyLandmarkOrientation,
    BodyStructure,
    BodyStructureCodeableReference,
    BodyStructureReference,
    DistanceFromLandmark,
    IncludedStructure,
)
from dfhir.devices.serializers import DeviceReferenceSerializer
from dfhir.imagingselections.serializers import ImagingSelectionReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer


class DistanceFromLandmarkSerializer(WritableNestedModelSerializer):
    """Distance from landmark serializer."""

    device = DeviceReferenceSerializer(many=True, required=False)
    value = QuantitySerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DistanceFromLandmark
        exclude = ["created_at", "updated_at"]


class BodyLandmarkOrientationSerializer(WritableNestedModelSerializer):
    """Body landmark orientation serializer."""

    landmark_description = CodeableConceptSerializer(many=True, required=False)
    clock_face_position = CodeableConceptSerializer(many=True, required=False)
    distance_from_landmark = DistanceFromLandmarkSerializer(many=True, required=False)
    surface_orientation = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = BodyLandmarkOrientation
        exclude = ["created_at", "updated_at"]


class IncludedStructureSerializer(WritableNestedModelSerializer):
    """Included structure serializer."""

    structure = CodeableConceptSerializer(many=False, required=False)
    laterality = CodeableConceptSerializer(many=False, required=False)
    body_landmark_orientation = BodyLandmarkOrientationSerializer(
        many=True, required=False
    )
    spatial_reference = ImagingSelectionReferenceSerializer(many=True, required=False)
    qualifier = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = IncludedStructure
        exclude = ["created_at", "updated_at"]


class BodyStructureReferenceSerializer(BaseReferenceModelSerializer):
    """Body structure reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = BodyStructureReference
        exclude = ["created_at", "updated_at"]


class BodyStructureSerializer(BaseWritableNestedModelSerializer):
    """Body structure serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    morphology = CodeableConceptSerializer(many=False, required=False)
    included_structure = IncludedStructureSerializer(many=True, required=False)
    excluded_structure = IncludedStructureSerializer(many=True, required=False)
    image = AttachmentSerializer(many=True, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = BodyStructure
        exclude = ["created_at", "updated_at"]


class BodyStructureCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Body structure codeable reference serializer."""

    reference = BodyStructureReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = BodyStructureCodeableReference
        exclude = ["created_at", "updated_at"]
