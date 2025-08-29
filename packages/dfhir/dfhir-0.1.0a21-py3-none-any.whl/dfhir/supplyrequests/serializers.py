"""supply request serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    QuantitySerializer,
    RangeSerializer,
    ReferenceSerializer,
)
from dfhir.patients.serializers import PatientReferenceSerializer
from dfhir.supplyrequests.models import (
    SupplyRequest,
    SupplyRequestDeliverFromReference,
    SupplyRequestDeliverToReference,
    SupplyRequestItemCodeableReference,
    SupplyRequestItemReference,
    SupplyRequestParameter,
    SupplyRequestReasonCodeableReference,
    SupplyRequestReasonReference,
    SupplyRequestReference,
    SupplyRequestRequesterReference,
    SupplyRequestSupplierReference,
)


class SupplyRequestParameterSerializer(WritableNestedModelSerializer):
    """supply request parameter serializer."""

    code = CodeableConceptSerializer(required=False)
    value_codeable_concept = CodeableConceptSerializer(required=False)
    value_quantity = QuantitySerializer(required=False)
    value_range = RangeSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequestParameter
        exclude = ["created_at", "updated_at"]


class SupplyRequestRequesterReferenceSerializer(BaseReferenceModelSerializer):
    """supply request requester reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequestRequesterReference
        exclude = ["created_at", "updated_at"]


class SupplyRequestReasonReferenceSerializer(BaseReferenceModelSerializer):
    """supply request reason reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequestReasonReference
        exclude = ["created_at", "updated_at"]


class SupplyRequestReasonCodeableReferenceSerializer(WritableNestedModelSerializer):
    """supply request reason codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = SupplyRequestReasonReferenceSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequestReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class SupplyRequestItemReferenceSerializer(BaseReferenceModelSerializer):
    """supply request item reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequestItemReference
        exclude = ["created_at", "updated_at"]


class SupplyRequestSupplierReferenceSerializer(BaseReferenceModelSerializer):
    """supply request supplier reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequestSupplierReference
        exclude = ["created_at", "updated_at"]


class SupplyRequestDeliverToReferenceSerializer(BaseReferenceModelSerializer):
    """supply request deliver to reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequestDeliverToReference
        exclude = ["created_at", "updated_at"]


class SupplyRequestDeliverFromReferenceSerializer(BaseReferenceModelSerializer):
    """supply request deliver from reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequestDeliverFromReference
        exclude = ["created_at", "updated_at"]


class SupplyRequestItemCodeableReferenceSerializer(WritableNestedModelSerializer):
    """supply request item codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = SupplyRequestItemReferenceSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequestItemCodeableReference
        exclude = ["created_at", "updated_at"]


class SupplyRequestSerializer(BaseWritableNestedModelSerializer):
    """supply request serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    based_on = ReferenceSerializer(required=False, many=True)
    category = CodeableConceptSerializer(required=False)
    deliver_for = PatientReferenceSerializer(required=False)
    item = SupplyRequestItemCodeableReferenceSerializer(required=False)
    quantity = QuantitySerializer(required=False)
    parameter = SupplyRequestParameterSerializer(required=False, many=True)
    occurrence_period = PeriodSerializer(required=False)
    occurrence_timing = PeriodSerializer(required=False)
    requester = SupplyRequestRequesterReferenceSerializer(required=False)
    supplier = SupplyRequestSupplierReferenceSerializer(required=False, many=True)
    reason = SupplyRequestReasonCodeableReferenceSerializer(required=False, many=True)
    deliver_from = SupplyRequestDeliverFromReferenceSerializer(required=False)
    deliver_to = SupplyRequestDeliverToReferenceSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequest
        exclude = ["created_at", "updated_at"]


class SupplyRequestReferenceSerilizer(BaseReferenceModelSerializer):
    """supply request reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = SupplyRequestReference
        exclude = ["created_at", "updated_at"]
