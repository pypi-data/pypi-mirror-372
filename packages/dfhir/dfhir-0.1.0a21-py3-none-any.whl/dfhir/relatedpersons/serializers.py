"""Related persons serializers."""

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
    PeriodSerializer,
)
from dfhir.patients.serializers import PatientReferenceSerializer

from .models import RelatedPerson, RelatedPersonReference


class RelatedPersonReferenceSerializer(BaseReferenceModelSerializer):
    """Related person reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = RelatedPersonReference
        exclude = ["created_at", "updated_at"]


class RelatedPersonSerializer(BaseWritableNestedModelSerializer):
    """Related person serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    relationship = CodeableConceptSerializer(many=True, required=False)
    patient = PatientReferenceSerializer(required=False)
    role = CodeableConceptSerializer(many=True, required=False)
    name = HumanNameSerializer(many=True, required=False)
    telecom = ContactPointSerializer(many=True, required=False)
    address = AddressSerializer(many=True, required=False)
    photo = AttachmentSerializer(many=True, required=False)
    period = PeriodSerializer(required=False)
    communication = CommunicationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = RelatedPerson
        exclude = ["created_at", "updated_at"]
