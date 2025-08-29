"""Patient serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

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
    PeriodSerializer,
)
from dfhir.practitioners.serializers import (
    PractitionerOrganizationPractitionerRoleReferenceSerializer,
)

from .models import (
    Patient,
    PatientContact,
    PatientGroupReference,
    PatientLink,
    PatientOrganizationReference,
    PatientPractitionerReference,
    PatientReference,
    PatientRelatedPersonReference,
)


class PatientReferenceSerializer(BaseReferenceModelSerializer):
    """Patient reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PatientReference
        exclude = ["created_at", "updated_at"]


class PatientGroupReferenceSerializer(BaseReferenceModelSerializer):
    """Patient group reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PatientGroupReference
        exclude = ["created_at", "updated_at"]


class PatientRelatedPersonReferenceSerializer(BaseReferenceModelSerializer):
    """Patient related person reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PatientRelatedPersonReference
        exclude = ["created_at", "updated_at"]


class PatientLinkSerializer(serializers.ModelSerializer):
    """Patient link serializer."""

    class Meta:
        """Meta class."""

        model = PatientLink
        exclude = ["created_at", "updated_at"]


class PatientContactSerializer(WritableNestedModelSerializer):
    """Patient contact serializer."""

    name = HumanNameSerializer(required=False)
    telecom = ContactPointSerializer(many=True, required=False)
    organization = OrganizationReferenceSerializer(required=False)
    period = PeriodSerializer(required=False)
    address = AddressSerializer(required=False)
    relationship = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = PatientContact
        exclude = ["created_at", "updated_at"]


class PatientSerializer(BaseWritableNestedModelSerializer):
    """Patient serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    name = HumanNameSerializer(many=True, required=False)
    telecom = ContactPointSerializer(many=True, required=False)
    marital_status = CodeableConceptSerializer(required=False)
    photo = AttachmentSerializer(many=True, required=False)
    communication = CommunicationSerializer(many=True, required=False)
    contact = PatientContactSerializer(many=True, required=False)
    general_practitioner = PractitionerOrganizationPractitionerRoleReferenceSerializer(
        required=False
    )
    address = AddressSerializer(many=True, required=False)
    managing_organization = OrganizationReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = Patient
        exclude = ["created_at", "updated_at"]


class PatientOrganizationReferenceSerializer(BaseReferenceModelSerializer):
    """Patient organization reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = PatientOrganizationReference
        exclude = ["created_at", "updated_at"]


class PatientPractitionerReferenceSerializer(BaseReferenceModelSerializer):
    """Patient Practitioner Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = PatientPractitionerReference
        exclude = ["created_at", "updated_at"]
