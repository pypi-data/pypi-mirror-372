"""Serializers for the communications app."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodeableReferenceSerializer,
    CodingSerializer,
    IdentifierSerializer,
    ReferenceSerializer,
)
from dfhir.communications.models import (
    Communication,
    CommunicationBsedOnReference,
    CommunicationPayload,
    CommunicationRecipientReference,
    CommunicationReference,
    CommunicationRequestReference,
    CommunicationSenderReference,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.patients.serializers import PatientGroupReferenceSerializer


class CommunicationRequestReferenceSerializer(BaseReferenceModelSerializer):
    """communication request reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = CommunicationRequestReference
        exclude = ["created_at", "updated_at"]


class CommunicationRecipientReferenceSerializer(BaseReferenceModelSerializer):
    """communication recipient reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = CommunicationRecipientReference
        exclude = ["created_at", "updated_at"]


class CommunicationPayloadSerializer(WritableNestedModelSerializer):
    """communication payload serializer."""

    content_attachment = AttachmentSerializer(many=False, required=False)
    content_reference = ReferenceSerializer(many=False, required=False)
    content_codeable_reference = CodeableReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = CommunicationPayload
        exclude = ["created_at", "updated_at"]


class CommunicationSenderReferenceSerializer(BaseReferenceModelSerializer):
    """communication sender reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = CommunicationSenderReference
        exclude = ["created_at", "updated_at"]


class CommunicationBsedOnReferenceSerializer(BaseReferenceModelSerializer):
    """communication based on reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = CommunicationBsedOnReference
        exclude = ["created_at", "updated_at"]


class CommunicationReferenceSerializer(BaseReferenceModelSerializer):
    """communication reference serializer."""

    class Meta:
        """Meta options."""

        model = CommunicationReference
        exclude = ["created_at", "updated_at"]


class CommunicationSerializer(BaseWritableNestedModelSerializer):
    """communication serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = CommunicationBsedOnReferenceSerializer(many=True, required=False)
    part_of = ReferenceSerializer(many=True, required=False)
    in_response_to = CommunicationReferenceSerializer(many=True, required=False)
    status = CodingSerializer(many=False, required=False)
    status_reason = CodeableConceptSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    medium = CodeableConceptSerializer(many=True, required=False)
    subject = PatientGroupReferenceSerializer(many=False, required=False)
    topic = CodeableConceptSerializer(many=False, required=False)
    about = ReferenceSerializer(many=True, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    recipient = CommunicationRecipientReferenceSerializer(many=True, required=False)
    sender = CommunicationSenderReferenceSerializer(many=False, required=False)
    reason = CodeableConceptSerializer(many=True, required=False)
    payload = CommunicationPayloadSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = Communication
        exclude = ["created_at", "updated_at"]
