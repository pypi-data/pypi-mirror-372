"""Organization serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    ExtendedContactDetailSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    QualificationSerializer,
)
from dfhir.endpoints.serializers import EndpointReferenceSerializer
from dfhir.organizations.models import Organization, OrganizationCodeableReference


class OrganizationSerializer(BaseWritableNestedModelSerializer):
    """Organization serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    contact = ExtendedContactDetailSerializer(many=True, required=False)
    qualification = QualificationSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    endpoint = EndpointReferenceSerializer(many=True, required=False)
    part_of = OrganizationReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Organization
        exclude = ["created_at", "updated_at"]


class OrganizationCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Organization codeable reference serializer."""

    reference = OrganizationReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = OrganizationCodeableReference
        exclude = ["created_at", "updated_at"]
