"""Invoices serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.accounts.serializers import AccountReferenceSerializer
from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    MonetaryComponentSerializer,
    MoneySerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
)
from dfhir.chargeitems.serializers import ChargeItemReferenceSerializer
from dfhir.invoices.models import (
    Invoice,
    InvoiceLineItem,
    InvoiceParticipant,
    InvoiceParticipantActorReference,
    InvoiceRecipientReference,
    InvoiceReference,
)
from dfhir.patients.serializers import PatientGroupReferenceSerializer


class InvoiceRecipientReferenceSerializer(BaseReferenceModelSerializer):
    """Invoice recipient reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = InvoiceRecipientReference
        exclude = ["created_at", "updated_at"]


class InvoiceParticipantActorReferenceSerializer(BaseReferenceModelSerializer):
    """Invoice participant actor reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = InvoiceParticipantActorReference
        exclude = ["created_at", "updated_at"]


class InvoiceParticipantSerializer(WritableNestedModelSerializer):
    """Invoice participant serializer."""

    role = CodeableConceptSerializer(many=False, required=False)
    actor = InvoiceParticipantActorReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = InvoiceParticipant
        exclude = ["created_at", "updated_at"]


class InvoiceLineItemSerializer(WritableNestedModelSerializer):
    """Invoice line item serializer."""

    service_period = PeriodSerializer(many=False, required=False)
    charge_item_reference = ChargeItemReferenceSerializer(many=False, required=False)
    charge_item_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    price_component = MonetaryComponentSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = InvoiceLineItem
        exclude = ["created_at", "updated_at"]


class InvoiceSerializer(BaseWritableNestedModelSerializer):
    """Invoice serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    subject = PatientGroupReferenceSerializer(many=False, required=False)
    recipient = InvoiceRecipientReferenceSerializer(many=False, required=False)
    period_period = PeriodSerializer(many=False, required=False)
    participant = InvoiceParticipantSerializer(many=True, required=False)
    issuer = OrganizationReferenceSerializer(many=False, required=False)
    account = AccountReferenceSerializer(many=False, required=False)
    line_item = InvoiceLineItemSerializer(many=True, required=False)
    total_price_component = MonetaryComponentSerializer(many=True, required=False)
    total_net = MoneySerializer(many=False, required=False)
    total_gross = MoneySerializer(many=False, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Invoice
        exclude = ["created_at", "updated_at"]


class InvoiceReferenceSerializer(BaseReferenceModelSerializer):
    """Invoice reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = InvoiceReference
        exclude = ["created_at", "updated_at"]
