"""inventory item serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    QuantitySerializer,
    RangeSerializer,
    RatioSerializer,
)
from dfhir.base.serializers import QuantitySerializer as DurationSerializer
from dfhir.inventoryitems.models import (
    InventoryItem,
    InventoryItemAssociation,
    InventoryItemAssociationTypeReference,
    InventoryItemCharacteristic,
    InventoryItemDescription,
    InventoryItemInstance,
    InventoryItemName,
    InventoryItemProductReference,
    InventoryItemReference,
    InventoryItemResponsibleOrganization,
)
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.patients.serializers import PatientOrganizationReferenceSerializer


class InventoryItemAssociationTypeReferenceSerializer(BaseReferenceModelSerializer):
    """inventory item association type reference serializer."""

    identifier = IdentifierSerializer(many=False, required=True)

    class Meta:
        """meta options."""

        model = InventoryItemAssociationTypeReference
        exclude = ["created_at", "updated_at"]


class InventoryItemName(serializers.ModelSerializer):
    """inventory item name serializer."""

    class Meta:
        """meta options."""

        model = InventoryItemName
        exclude = ["created_at", "updated_at"]


class InventoryItemResponsibleAssociationSerializer(WritableNestedModelSerializer):
    """inventory item responsible association serializer."""

    code = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = InventoryItemResponsibleOrganization
        exclude = ["created_at", "updated_at"]


class InventoryItemDescriptionSerializer(serializers.ModelSerializer):
    """inventory item description serializer."""

    class Meta:
        """meta options."""

        model = InventoryItemDescription
        exclude = ["created_at", "updated_at"]


class InventoryItemAssociationSerializer(WritableNestedModelSerializer):
    """inventory item association serializer."""

    association_type = CodeableConceptSerializer(many=False, required=False)
    related_item = InventoryItemAssociationTypeReferenceSerializer(
        many=False, required=False
    )
    quantity = RatioSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = InventoryItemAssociation
        exclude = ["created_at", "updated_at"]


class InventoryItemCharacteristicSerializer(WritableNestedModelSerializer):
    """inventory item characteristic serializer."""

    characteristic_type = CodeableConceptSerializer(many=False, required=False)
    value_quantity = QuantitySerializer(many=False, required=False)
    value_range = RangeSerializer(many=False, required=False)
    value_ratio = RatioSerializer(many=False, required=False)
    value_annotation = AnnotationSerializer(many=False, required=False)
    value_duration = DurationSerializer(many=False, required=False)
    value_codeable_concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = InventoryItemCharacteristic
        exclude = ["created_at", "updated_at"]


class InventoryItemInstanceSerializer(WritableNestedModelSerializer):
    """inventory item instance serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    subject = PatientOrganizationReferenceSerializer(many=False, required=False)
    location = LocationReferenceSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = InventoryItemInstance
        exclude = ["created_at", "updated_at"]


class InventoryItemProductReference(BaseReferenceModelSerializer):
    """inventory item product reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = InventoryItemProductReference
        exclude = ["created_at", "updated_at"]


class InventoryItemSerializer(BaseWritableNestedModelSerializer):
    """inventory item serializer."""

    identifier = IdentifierSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    code = CodeableConceptSerializer(many=True, required=False)
    name = InventoryItemName(many=True, required=False)
    responsible_organization = InventoryItemResponsibleAssociationSerializer(
        many=True, required=False
    )
    description = InventoryItemDescriptionSerializer(many=False, required=False)
    inventory_status = CodeableConceptSerializer(many=False, required=False)
    base_unit = CodeableConceptSerializer(many=False, required=False)
    net_content = QuantitySerializer(many=False, required=False)
    association = InventoryItemAssociationSerializer(many=True, required=False)
    characteristic = InventoryItemCharacteristicSerializer(many=True, required=False)
    instance = InventoryItemInstanceSerializer(many=False, required=False)
    product_reference = InventoryItemProductReference(many=False, required=False)

    class Meta:
        """meta options."""

        model = InventoryItem
        exclude = ["created_at", "updated_at"]


class InventoryItemReferenceSerializer(BaseReferenceModelSerializer):
    """inventory item reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = InventoryItemReference
        exclude = ["created_at", "updated_at"]
