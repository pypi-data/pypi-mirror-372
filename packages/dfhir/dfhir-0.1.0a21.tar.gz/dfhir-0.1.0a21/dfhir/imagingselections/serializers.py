"""image selection serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
)
from dfhir.endpoints.serializers import EndpointReferenceSerializer
from dfhir.imagingselections.models import (
    ImagingSelection,
    ImagingSelectionBasedOnReference,
    ImagingSelectionCodeableReference,
    ImagingSelectionImageRegion3D,
    ImagingSelectionInstance,
    ImagingSelectionInstanceImagingRegion2D,
    ImagingSelectionPerformer,
    ImagingSelectionPerformerActorReference,
    ImagingSelectionReference,
    ImagingSelectionSubjectReference,
)

# from dfhir.imagingstudies.serializers import ImagingStudyReferenceSerializer


class ImagingSelectionPerformerActorReferenceSerializer(BaseReferenceModelSerializer):
    """image selection performer actor reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ImagingSelectionPerformerActorReference
        exclude = ["created_at", "updated_at"]


class ImagingSelectionPerformerSerializer(WritableNestedModelSerializer):
    """image selection performer serializer."""

    function = CodeableConceptSerializer(required=False)
    actor = ImagingSelectionPerformerActorReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = ImagingSelectionPerformer
        exclude = ["created_at", "updated_at"]


class ImagingSelectionBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """image selection based on reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ImagingSelectionBasedOnReference
        exclude = ["created_at", "updated_at"]


class ImagingSelectionInstanceImagingRegion2DSerializer(serializers.ModelSerializer):
    """image selection instance imaging region 2d serializer."""

    class Meta:
        """meta options."""

        model = ImagingSelectionInstanceImagingRegion2D
        exclude = ["created_at", "updated_at"]


class ImagingSelectionInstanceSerializer(WritableNestedModelSerializer):
    """imaging selection instance serializer."""

    imaging_region = ImagingSelectionInstanceImagingRegion2DSerializer(
        many=True, required=False
    )

    class Meta:
        """meta options."""

        model = ImagingSelectionInstance
        exclude = ["created_at", "updated_at"]


class ImagingSelectionImageRegion3DSerializer(serializers.ModelSerializer):
    """image selection image region 3d serializer."""

    class Meta:
        """meta options."""

        model = ImagingSelectionImageRegion3D
        exclude = ["created_at", "updated_at"]


class ImagingSelectionSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """image selection subject reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ImagingSelectionSubjectReference
        exclude = ["created_at", "updated_at"]


class ImagingSelectionReferenceSerializer(BaseReferenceModelSerializer):
    """image selection reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = ImagingSelectionReference
        exclude = ["created_at", "updated_at"]


class ImagingSelectionSerializer(WritableNestedModelSerializer):
    """image selection serializer."""

    def get_fields(self):
        """Get fields."""
        from dfhir.bodystructures.serializers import (
            BodyStructureCodeableReferenceSerializer,
        )
        from dfhir.imagingstudies.serializers import ImagingStudyReferenceSerializer

        fields = super().get_fields()
        fields["body_site"] = BodyStructureCodeableReferenceSerializer(
            many=True, required=False
        )
        fields["derived_from"] = ImagingStudyReferenceSerializer(required=False)
        return fields

    identifier = IdentifierSerializer(many=True, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    code = CodeableConceptSerializer(required=False)
    subject = ImagingSelectionSubjectReferenceSerializer(many=False, required=False)
    performer = ImagingSelectionPerformerSerializer(many=True, required=False)
    based_on = ImagingSelectionBasedOnReferenceSerializer(many=True, required=False)
    focus = ImagingSelectionReferenceSerializer(many=True, required=False)
    endpoint = EndpointReferenceSerializer(many=True, required=False)
    instance = ImagingSelectionInstanceSerializer(many=True, required=False)
    image_region_3d = ImagingSelectionImageRegion3DSerializer(many=True, required=False)

    class Meta:
        """Meta."""

        model = ImagingSelection
        exclude = ["created_at", "updated_at"]


class ImagingSelectionCodeablereferenceSerializer(WritableNestedModelSerializer):
    """image selection codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = ImagingSelectionReferenceSerializer(required=False)

    class Meta:
        """Meta."""

        model = ImagingSelectionCodeableReference
        exclude = ["created_at", "updated_at"]
