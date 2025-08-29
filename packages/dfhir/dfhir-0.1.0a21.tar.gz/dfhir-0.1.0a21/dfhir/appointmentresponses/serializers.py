"""Appointment Responses Serializers."""

from dfhir.appointments.serializers import AppointmentReferenceSerializer
from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
)

from .models import (
    AppointmentResponse,
    AppointmentResponseActorReference,
)


class AppointmentResponseActorReferenceSerializer(BaseReferenceModelSerializer):
    """Appointment response actor reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = AppointmentResponseActorReference
        exclude = ["created_at", "updated_at"]


class AppointmentResponseSerializer(BaseWritableNestedModelSerializer):
    """Appointment response serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    appointment = AppointmentReferenceSerializer(many=False, required=False)
    participant_type = CodeableConceptSerializer(many=True, required=False)
    actor = AppointmentResponseActorReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = AppointmentResponse
        exclude = ["created_at", "updated_at"]
