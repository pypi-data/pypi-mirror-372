"""Location serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework.serializers import ModelSerializer

from dfhir.base.serializers import (
    AddressSerializer,
    AvailabilitySerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodingSerializer,
    ExtendedContactDetailSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    VirtualServiceDetailsSerializer,
)
from dfhir.endpoints.serializers import EndpointReferenceSerializer

from .models import (
    Location,
    LocationCodeableReference,
    LocationOrganizationReference,
    LocationReference,
    Position,
)


class LocationReferenceSerializer(BaseReferenceModelSerializer):
    """Location reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = LocationReference
        exclude = ["created_at", "updated_at"]


class LocationOrganizationReferenceSerializer(BaseReferenceModelSerializer):
    """Location organization reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = LocationOrganizationReference
        exclude = ["created_at", "updated_at"]


class PositionSerializer(ModelSerializer):
    """Position serializer."""

    class Meta:
        """Meta class."""

        model = Position
        exclude = ["created_at", "updated_at"]


class LocationSerializer(BaseWritableNestedModelSerializer):
    """Location serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    position = PositionSerializer(many=False, required=False)
    operational_status = CodingSerializer(many=False, required=False)
    contact = ExtendedContactDetailSerializer(many=True, required=False)
    address = AddressSerializer(many=False, required=False)
    hours_of_operation = AvailabilitySerializer(many=False, required=False)
    form = CodeableConceptSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    managing_organization = OrganizationReferenceSerializer(many=False, required=False)
    characteristic = CodeableConceptSerializer(many=True, required=False)
    virtual_service = VirtualServiceDetailsSerializer(many=True, required=False)
    endpoint = EndpointReferenceSerializer(many=True, required=False)
    part_of = LocationReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Location
        exclude = ["created_at", "updated_at"]


class LocationCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Location codeable reference serializer."""

    concept = CodeableConceptSerializer(many=False, required=False)
    reference = LocationReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = LocationCodeableReference
        exclude = ["created_at", "updated_at"]
