"""inventory report serializer."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    QuantitySerializer,
)
from dfhir.inventoryreports.models import (
    InventoryReport,
    InventoryReportInventoryListing,
    InventoryReportInventoryListingItem,
    InventoryReportInventoryListingItemItemCodeableReference,
    InventoryReportInventoryListingItemItemReference,
    InventoryReportReporterReference,
)
from dfhir.locations.serializers import LocationReferenceSerializer


class InventoryReportReporterReferenceSerializer(BaseReferenceModelSerializer):
    """inventory report reporter reference serializer."""

    identifier = IdentifierSerializer(required=True)

    class Meta:
        """meta options."""

        model = InventoryReportReporterReference
        exclude = ["created_at", "updated_at"]


class InventoryReportInventoryListingItemItemReferenceSerializer(
    BaseReferenceModelSerializer
):
    """inventory report listing item item reference serializer."""

    identifier = IdentifierSerializer(required=True)

    class Meta:
        """meta options."""

        model = InventoryReportInventoryListingItemItemReference
        exclude = ["created_at", "updated_at"]


class InventoryReportInventoryListingItemItemCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """inventory report listing item item codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = InventoryReportInventoryListingItemItemReferenceSerializer(
        required=False
    )

    class Meta:
        """meta options."""

        model = InventoryReportInventoryListingItemItemCodeableReference
        exclude = ["created_at", "updated_at"]


class InventoryReportInventoryListingItemSerializer(WritableNestedModelSerializer):
    """inventory report inventory listing item serializer."""

    category = CodeableConceptSerializer(required=False)
    quantity = QuantitySerializer(required=False)
    item = InventoryReportInventoryListingItemItemReferenceSerializer(
        required=False, many=True
    )

    class Meta:
        """meta options."""

        model = InventoryReportInventoryListingItem
        exclude = ["created_at", "updated_at"]


class InventoryReportInventoryListingSerializer(WritableNestedModelSerializer):
    """inventory report listing serializer."""

    location = LocationReferenceSerializer(required=False)
    item_status = CodeableConceptSerializer(required=False)
    item = InventoryReportInventoryListingItemItemCodeableReferenceSerializer(
        required=False, many=True
    )

    class Meta:
        """meta options."""

        model = InventoryReportInventoryListing
        exclude = ["created_at", "updated_at"]


class InventoryReportSerializer(BaseWritableNestedModelSerializer):
    """inventory report serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    operation_type = CodeableConceptSerializer(required=False)
    operation_type_reason = CodeableConceptSerializer(required=False)
    reporter = InventoryReportReporterReferenceSerializer(required=False)
    reporting_period = PeriodSerializer(required=False)
    inventory_listing = InventoryReportInventoryListingSerializer(
        required=False, many=True
    )
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = InventoryReport
        exclude = ["created_at", "updated_at"]
