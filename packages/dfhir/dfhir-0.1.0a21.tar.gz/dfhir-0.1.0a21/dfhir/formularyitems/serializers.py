"""formulary item serializers."""

from dfhir.base.serializers import (
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
)
from dfhir.formularyitems.models import FormularyItem, FormularyItemReference


class FormularyItemSerializer(BaseWritableNestedModelSerializer):
    """formulary item serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    code = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta options."""

        model = FormularyItem
        exclude = ["created_at", "updated_at"]


class FormularyItemReferenceSerializer(BaseWritableNestedModelSerializer):
    """formulary item reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = FormularyItemReference
        exclude = ["created_at", "updated_at"]
