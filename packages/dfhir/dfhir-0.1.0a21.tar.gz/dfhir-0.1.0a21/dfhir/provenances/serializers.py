"""provenance serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    ReferenceSerializer,
)
from dfhir.provenances.models import (
    Provenance,
    ProvenanceAgent,
    ProvenanceAgentOnBehalfOf,
    ProvenanceAgentWhoReference,
    ProvenanceEntry,
    ProvenanceReference,
)


class ProvenanceWhoReferenceSerializer(BaseReferenceModelSerializer):
    """provenance who reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ProvenanceAgentWhoReference
        exclude = ["created_at", "updated_at"]


class ProvenanceAgentOnBehalfOfSerializer(BaseReferenceModelSerializer):
    """Provenance agent on behalf of serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ProvenanceAgentOnBehalfOf
        exclude = ["created_at", "updated_at"]


class ProvenanceAgentSerializer(WritableNestedModelSerializer):
    """provenance agent serializer."""

    type = CodeableConceptSerializer(required=False)
    role = CodeableConceptSerializer(required=False)
    who = ProvenanceWhoReferenceSerializer(many=False, required=False)
    on_behalf_of = ProvenanceAgentOnBehalfOfSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ProvenanceAgent
        exclude = ["created_at", "updated_at"]


class ProvenanceEntrySerializer(WritableNestedModelSerializer):
    """provenance entry serializer."""

    what = ReferenceSerializer(many=False, required=False)
    agent = ProvenanceAgentSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ProvenanceEntry
        exclude = ["created_at", "updated_at"]


class ProvenanceReferenceSerializer(BaseReferenceModelSerializer):
    """Provenance reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ProvenanceReference
        exclude = ["created_at", "updated_at"]


class ProvenanceSerializer(BaseWritableNestedModelSerializer):
    """Provenance serializer."""

    target = ProvenanceReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Provenance
        exclude = ["created_at", "updated_at"]
