"""Payment Notices serializers."""

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    MoneySerializer,
    OrganizationReferenceSerializer,
)

from ..paymentreconciliations.serializers import (
    PaymentReconciliationReferenceSerializer,
)
from .models import (
    PaymentNotice,
    PaymentNoticePayeeReference,
    PaymentNoticeReporterReference,
    PaymentNoticeRequestReference,
    PaymentNoticeResponseReference,
)


class PaymentNoticeReporterReferenceSerializer(BaseReferenceModelSerializer):
    """Payment Notice Reporter Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PaymentNoticeReporterReference
        exclude = ["created_at", "updated_at"]


class PaymentNoticePayeeReferenceSerializer(BaseReferenceModelSerializer):
    """Payment Notice Payee Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PaymentNoticePayeeReference
        exclude = ["created_at", "updated_at"]


class PaymentNoticeRequestReferenceSerializer(BaseReferenceModelSerializer):
    """Payment Notice Request Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PaymentNoticeRequestReference
        exclude = ["created_at", "updated_at"]


class PaymentNoticeResponseReferenceSerializer(BaseReferenceModelSerializer):
    """Payment Notice Response Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PaymentNoticeResponseReference
        exclude = ["created_at", "updated_at"]


class PaymentNoticeSerializer(BaseWritableNestedModelSerializer):
    """Payment Notice Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    request = PaymentNoticeRequestReferenceSerializer(many=False, required=False)
    response = PaymentNoticeResponseReferenceSerializer(many=False, required=False)
    reporter = PaymentNoticeReporterReferenceSerializer(many=False, required=False)
    payment = PaymentReconciliationReferenceSerializer(many=False, required=False)
    payee = PaymentNoticePayeeReferenceSerializer(many=False, required=False)
    recipient = OrganizationReferenceSerializer(many=False, required=False)
    amount = MoneySerializer(many=False, required=False)
    payment_status = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PaymentNotice
        exclude = ["created_at", "updated_at"]
