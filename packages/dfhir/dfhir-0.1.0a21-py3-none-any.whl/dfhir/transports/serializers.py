"""transport serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    ReferenceSerializer,
)
from dfhir.coverages.serializers import CoverageClaimResponseReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.provenances.serializers import ProvenanceReferenceSerializer
from dfhir.transports.models import (
    Transport,
    TransportBasedOnReference,
    TransportInput,
    TransportOutput,
    TransportOwnerReference,
    TransportReference,
    TransportRequesterReference,
    TransportRestriction,
    TransportRestrictionRecipientReference,
)


class TransportReferenceSerializer(BaseReferenceModelSerializer):
    """Transport Reference Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta."""

        model = TransportReference
        exclude = ["created_at", "updated_at"]


class TransportBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """Transport Based On Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta."""

        model = TransportBasedOnReference
        exclude = ["created_at", "updated_at"]


class TransportOwnerReferenceSerializer(BaseReferenceModelSerializer):
    """TransportOwnerReferenceSerializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta."""

        model = TransportOwnerReference
        exclude = ["created_at", "updated_at"]


class TransportRestrictionRecipientReferenceSerializer(BaseReferenceModelSerializer):
    """Transport Restriction Recipient Reference Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta."""

        model = TransportRestrictionRecipientReference
        exclude = ["created_at", "updated_at"]


class TransportRestrictionSerializer(WritableNestedModelSerializer):
    """TransportRestrictionSerializer."""

    period = PeriodSerializer(required=False)
    recipient = TransportRestrictionRecipientReferenceSerializer(
        required=False, many=True
    )

    class Meta:
        """Meta."""

        model = TransportRestriction
        exclude = ["created_at", "updated_at"]


class TransportInputSerializer(WritableNestedModelSerializer):
    """TransportInputSerializer."""

    type = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta."""

        model = TransportInput
        exclude = ["created_at", "updated_at"]


class TransportOutputSerializer(WritableNestedModelSerializer):
    """TransportOutputSerializer."""

    type = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta."""

        model = TransportOutput
        exclude = ["created_at", "updated_at"]


class TransportRequesterReferenceSerializer(BaseReferenceModelSerializer):
    """TransportRequesterReferenceSerializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta."""

        model = TransportRequesterReference
        exclude = ["created_at", "updated_at"]


class TransportSerializer(BaseWritableNestedModelSerializer):
    """transport serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = TransportBasedOnReferenceSerializer(required=False, many=True)
    group_identifier = IdentifierSerializer(required=False)
    part_of = TransportReferenceSerializer(required=False, many=True)
    status_reason = CodeableConceptSerializer(required=False)
    code = CodeableConceptSerializer(required=False)
    focus = ReferenceSerializer(required=False)
    for_value = ReferenceSerializer(required=False)
    encounter = EncounterReferenceSerializer(required=False)
    requester = TransportRequesterReferenceSerializer(required=False)
    performer_type = CodeableConceptSerializer(required=False, many=True)
    owner = TransportOwnerReferenceSerializer(required=False)
    location = LocationReferenceSerializer(required=False)
    insurance = CoverageClaimResponseReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    relevant_history = ProvenanceReferenceSerializer(many=True, required=False)
    restriction = TransportRestrictionSerializer(required=False)
    input = TransportInputSerializer(many=True, required=False)
    output = TransportOutputSerializer(many=True, required=False)
    requested_location = LocationReferenceSerializer(required=False)
    current_location = LocationReferenceSerializer(required=False)
    reason = CodeableConceptSerializer(required=False)
    history = TransportReferenceSerializer(required=False)

    class Meta:
        """Meta."""

        model = Transport
        exclude = ["created_at", "updated_at"]
        rename_fields = {
            "for_value": "for",
        }
