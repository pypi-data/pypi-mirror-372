"""Slot serializer module."""

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
)
from dfhir.healthcareservices.serializers import (
    HealthCareServiceCodeableReferenceSerializer,
)

from .models import Slot, SlotReference


class SlotReferenceSerializer(BaseReferenceModelSerializer):
    """Slot reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = SlotReference
        exclude = ["created_at", "updated_at"]


class SlotSerializer(BaseWritableNestedModelSerializer):
    """Slot serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    service_type = HealthCareServiceCodeableReferenceSerializer(
        many=True, required=False
    )
    specialty = CodeableConceptSerializer(many=True, required=False)
    service_category = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Slot
        exclude = ["created_at", "updated_at"]
