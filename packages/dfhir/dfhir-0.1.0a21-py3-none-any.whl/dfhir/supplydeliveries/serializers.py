"""supply delivery serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    SimpleQuantitySerializer,
    TimingSerializer,
)
from dfhir.patients.serializers import PatientReferenceSerializer
from dfhir.supplydeliveries.models import (
    SupplyDeliverReference,
    SupplyDelivery,
    SupplyDeliveryContractReference,
    SupplyDeliveryDestinationReference,
    SupplyDeliveryReceiverReference,
    SupplyDeliverySuppliedItem,
    SupplyDeliverySuppliedItemItemReference,
    SupplyDeliverySupplierReference,
)
from dfhir.supplyrequests.serializers import SupplyRequestReferenceSerilizer


class SupplyDeliveryContractReferenceSerializer(BaseReferenceModelSerializer):
    """supply delivery contract reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = SupplyDeliveryContractReference
        exclude = ["created_at", "updated_at"]


class SupplyDeliveryReferenceSerializer(BaseReferenceModelSerializer):
    """supply delivery reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = SupplyDeliverReference
        exclude = ["created_at", "updated_at"]


class SupplyDeliveryReceiverReferenceSerializer(BaseReferenceModelSerializer):
    """supply delivery receiver reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = SupplyDeliveryReceiverReference
        exclude = ["created_at", "updated_at"]


class SupplyDeliverySupplierReferenceSerializer(BaseReferenceModelSerializer):
    """supply delivery supplier reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = SupplyDeliverySupplierReference
        exclude = ["created_at", "updated_at"]


class SupplyDeliveryDestinationReferenceSerializer(BaseReferenceModelSerializer):
    """supply delivery destination reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = SupplyDeliveryDestinationReference
        exclude = ["created_at", "updated_at"]


class SupplyDeliverySuppliedItemItemReferenceSerializer(BaseReferenceModelSerializer):
    """supply delivery supplied item item reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = SupplyDeliverySuppliedItemItemReference
        exclude = ["created_at", "updated_at"]


class SupplyDeliverySuppliedItemSerializer(WritableNestedModelSerializer):
    """supply delivery supplied item serializer."""

    quantity = SimpleQuantitySerializer(required=False)
    condition = CodeableConceptSerializer(required=False)
    item_codeable_concept = CodeableConceptSerializer(required=False)
    item_reference = SupplyDeliverySuppliedItemItemReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = SupplyDeliverySuppliedItem
        exclude = ["created_at", "updated_at"]


class SupplyDeliverySerializer(BaseWritableNestedModelSerializer):
    """supply delivery serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    based_on = SupplyRequestReferenceSerilizer(required=False, many=True)
    part_of = SupplyDeliveryContractReferenceSerializer(required=False, many=True)
    patient = PatientReferenceSerializer(required=False)
    type = CodeableConceptSerializer(required=False)
    stage = CodeableConceptSerializer(required=False)
    supplied_item = SupplyDeliverySuppliedItemSerializer(required=False, many=True)
    occurrence_period = PeriodSerializer(required=False)
    occurrence_timing = TimingSerializer(required=False)
    supplier = SupplyDeliverySupplierReferenceSerializer(required=False)
    destination = SupplyDeliveryDestinationReferenceSerializer(required=False)
    receiver = SupplyDeliveryReceiverReferenceSerializer(required=False, many=True)

    class Meta:
        """meta options."""

        model = SupplyDelivery
        exclude = ["created_at", "updated_at"]
