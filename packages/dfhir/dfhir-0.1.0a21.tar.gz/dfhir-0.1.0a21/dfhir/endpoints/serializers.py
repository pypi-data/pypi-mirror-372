"""Endpoint serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AvailabilitySerializer,
    BaseReferenceModelSerializer,
    CodeableConceptSerializer,
    ContactPointSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
)

from .models import Endpoint, EndpointPayload, EndpointReference


class EndpointPayloadSerializer(WritableNestedModelSerializer):
    """Endpoint Payload serializer."""

    type = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = EndpointPayload
        exclude = ["created_at", "updated_at"]


class EndpointSerializer(WritableNestedModelSerializer):
    """Endpoint serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    payload = EndpointPayloadSerializer(many=True, required=False)
    contact = ContactPointSerializer(many=True, required=False)
    connection_type = CodeableConceptSerializer(many=True, required=False)
    environmental_type = CodeableConceptSerializer(many=True, required=False)
    managing_organization = OrganizationReferenceSerializer(many=False, required=False)
    availability = AvailabilitySerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Endpoint
        exclude = ["created_at", "updated_at"]


class EndpointReferenceSerializer(BaseReferenceModelSerializer):
    """EndpointReference serializer."""

    class Meta:
        """Meta class."""

        model = EndpointReference
        exclude = ["created_at", "updated_at", "endpoint"]
