"""Practitioner serializers."""

from dfhir.base.serializers import (
    AddressSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CommunicationSerializer,
    ContactPointSerializer,
    HumanNameSerializer,
    IdentifierSerializer,
    QualificationSerializer,
)

from .models import (
    Practitioner,
    PractitionerOrganizationPractitionerRoleReference,
    PractitionerPractitionerRoleReference,
    PractitionerReference,
)


class PractitionerReferenceSerializer(BaseReferenceModelSerializer):
    """Practitioner reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PractitionerReference
        exclude = ["created_at", "updated_at"]


class PractitionerSerializer(BaseWritableNestedModelSerializer):
    """Practitioner serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    name = HumanNameSerializer(many=True, required=False)
    telecom = ContactPointSerializer(many=True, required=False)
    photo = AttachmentSerializer(many=True, required=False)
    communication = CommunicationSerializer(many=True, required=False)
    qualification = QualificationSerializer(many=True, required=False)
    address = AddressSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Practitioner
        exclude = ["created_at", "updated_at"]


class PractitionerPractitionerRoleReferenceSerializer(BaseReferenceModelSerializer):
    """Practitioner Practitioner Role reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PractitionerPractitionerRoleReference
        exclude = ["created_at", "updated_at"]


class PractitionerOrganizationPractitionerRoleReferenceSerializer(
    BaseReferenceModelSerializer
):
    """practitioner organization practitioner role reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = PractitionerOrganizationPractitionerRoleReference
        exclude = ["created_at", "updated_at"]
