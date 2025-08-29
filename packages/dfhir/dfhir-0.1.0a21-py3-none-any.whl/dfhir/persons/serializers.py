"""Serializers for persons app."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AddressSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CommunicationSerializer,
    ContactPointSerializer,
    HumanNameSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
)

from .models import (
    Person,
    PersonLink,
    PersonLinkTargetReference,
    PersonReference,
)


class PersonLinkTargetReferenceSerializer(BaseReferenceModelSerializer):
    """PersonLinkTargetReferenceSerializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class for PersonLinkTargetReferenceSerializer."""

        model = PersonLinkTargetReference
        exclude = ["created_at", "updated_at"]


class PersonLinkSerializer(WritableNestedModelSerializer):
    """PersonLinkSerializer."""

    target = PersonLinkTargetReferenceSerializer(required=False)

    class Meta:
        """Meta class for PersonLinkSerializer."""

        model = PersonLink
        exclude = ["created_at", "updated_at"]


class PersonReferenceSerializer(BaseReferenceModelSerializer):
    """PersonReferenceSerializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class for PersonReferenceSerializer."""

        model = PersonReference
        exclude = ["created_at", "updated_at"]


class PersonSerializer(BaseWritableNestedModelSerializer):
    """PersonSerializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    name = HumanNameSerializer(required=False, many=True)
    telecom = ContactPointSerializer(required=False, many=True)
    address = AddressSerializer(required=False, many=True)
    marital_status = CodeableConceptSerializer(required=False)
    photo = AttachmentSerializer(required=False, many=True)
    communication = CommunicationSerializer(required=False, many=True)
    managing_organization = OrganizationReferenceSerializer(required=False)
    link = PersonLinkSerializer(required=False, many=True)

    class Meta:
        """Meta class for PersonSerializer."""

        model = Person
        exclude = ["created_at", "updated_at"]
