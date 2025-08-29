"""Device definitions serializer."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AttachmentSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodingSerializer,
    ContactDetailSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    ProductShelfLifeSerializer,
    QuantitySerializer,
    RangeSerializer,
    RatioSerializer,
    RelatedArtifactSerializer,
    UsageContextSerializer,
)

from .models import (
    DeviceDefinition,
    DeviceDefinitionChargeItem,
    DeviceDefinitionClassification,
    DeviceDefinitionCodeableReference,
    DeviceDefinitionConformsTo,
    DeviceDefinitionCorrectiveAction,
    DeviceDefinitionDeviceName,
    DeviceDefinitionDeviceVersion,
    DeviceDefinitionGuideline,
    DeviceDefinitionHasPart,
    DeviceDefinitionLink,
    DeviceDefinitionMarketDistribution,
    DeviceDefinitionMaterial,
    DeviceDefinitionPackaging,
    DeviceDefinitionPackagingDistributor,
    DeviceDefinitionProperty,
    DeviceDefinitionReference,
    DeviceDefinitionRegulatoryIdentifier,
    DeviceDefinitionUdiDeviceIdentifier,
)


class DeviceDefinitionRegulatoryIdentifierSerializer(WritableNestedModelSerializer):
    """Device Definition Regulatory Identifier serializer."""

    class Meta:
        """Meta class."""

        model = DeviceDefinitionRegulatoryIdentifier
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionPropertySerializer(WritableNestedModelSerializer):
    """Device Definition Property serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    value_quantity = QuantitySerializer(many=False, required=False)
    value_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    value_range = RangeSerializer(many=False, required=False)
    value_ratio = RatioSerializer(many=False, required=False)
    value_attachment = AttachmentSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionProperty
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionMarketDistributionSerializer(WritableNestedModelSerializer):
    """Device Definition Market Distribution serializer."""

    market_period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionMarketDistribution
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionUdiDeviceIdentifierSerializer(WritableNestedModelSerializer):
    """Device Definition UDI Device Identifier serializer."""

    market_distribution = DeviceDefinitionMarketDistributionSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = DeviceDefinitionUdiDeviceIdentifier
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionDeviceVersionSerializer(WritableNestedModelSerializer):
    """Device Version serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    component = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionDeviceVersion
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionReferenceSerializer(WritableNestedModelSerializer):
    """Device Definition Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionReference
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Device Definition Codeable Reference serializer."""

    reference = DeviceDefinitionReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionCodeableReference
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionLinkSerializer(WritableNestedModelSerializer):
    """Device Definition Link serializer."""

    relation = CodingSerializer(many=False, required=False)
    related_device = DeviceDefinitionCodeableReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = DeviceDefinitionLink
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionMaterialSerializer(WritableNestedModelSerializer):
    """Device Definition Material serializer."""

    substance = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionMaterial
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionClassificationSerializer(WritableNestedModelSerializer):
    """Device Definition Classification serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    justification = RelatedArtifactSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionClassification
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionGuidelineSerializer(WritableNestedModelSerializer):
    """Device Definition Guideline serializer."""

    use_context = UsageContextSerializer(many=True, required=False)
    related_artifact = RelatedArtifactSerializer(many=True, required=False)
    indication = CodeableConceptSerializer(many=True, required=False)
    contraindication = CodeableConceptSerializer(many=True, required=False)
    warning = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionGuideline
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionPackagingDistributorSerializer(WritableNestedModelSerializer):
    """Device Definition Packaging Distributor serializer."""

    organization_reference = OrganizationReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionPackagingDistributor
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionPackagingSerializer(WritableNestedModelSerializer):
    """Device Definition Packaging serializer."""

    identifier = IdentifierSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    distributor = DeviceDefinitionPackagingDistributorSerializer(
        many=True, required=False
    )
    udi_device_identifier = DeviceDefinitionUdiDeviceIdentifierSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = DeviceDefinitionPackaging
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionHasPartSerializer(WritableNestedModelSerializer):
    """Device Definition Has Part serializer."""

    reference = DeviceDefinitionReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionHasPart
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionDeviceNameSerializer(WritableNestedModelSerializer):
    """Device Definition Device Name serializer."""

    type = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionDeviceName
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionChargeItemSerializer(WritableNestedModelSerializer):
    """Device Definition Charge Item serializer."""

    count = QuantitySerializer(many=False, required=False)
    effective_period = PeriodSerializer(many=False, required=False)
    use_context = UsageContextSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionChargeItem
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionConformsToSerializer(WritableNestedModelSerializer):
    """Device Definition Conforms To serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    specification = CodeableConceptSerializer(many=False, required=False)
    source = RelatedArtifactSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionConformsTo
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionCorrectiveActionSerializer(WritableNestedModelSerializer):
    """Device Definition Corrective Action serializer."""

    period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinitionCorrectiveAction
        exclude = ["created_at", "updated_at"]


class DeviceDefinitionSerializer(BaseWritableNestedModelSerializer):
    """Device Definition serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    udiDeviceIdentifier = DeviceDefinitionUdiDeviceIdentifierSerializer(
        many=True, required=False
    )
    regulatory_identifier = DeviceDefinitionRegulatoryIdentifierSerializer(
        many=True, required=False
    )
    manufacturer = OrganizationReferenceSerializer(many=False, required=False)
    device_name = DeviceDefinitionDeviceNameSerializer(many=True, required=False)
    contact = ContactDetailSerializer(many=True, required=False)
    classification = DeviceDefinitionClassificationSerializer(many=True, required=False)
    conforms_to = DeviceDefinitionConformsToSerializer(many=True, required=False)
    has_part = DeviceDefinitionHasPartSerializer(many=True, required=False)
    packaging = DeviceDefinitionPackagingSerializer(many=True, required=False)
    device_version = DeviceDefinitionDeviceVersionSerializer(many=True, required=False)
    safety = CodeableConceptSerializer(many=True, required=False)
    shelf_life_storage = ProductShelfLifeSerializer(many=False, required=False)
    language_code = CodeableConceptSerializer(many=False, required=False)
    property = DeviceDefinitionPropertySerializer(many=True, required=False)
    link = DeviceDefinitionLinkSerializer(many=True, required=False)
    material = DeviceDefinitionMaterialSerializer(many=True, required=False)
    guideline = DeviceDefinitionGuidelineSerializer(many=False, required=False)
    corrective_action = DeviceDefinitionCorrectiveActionSerializer(
        many=False, required=False
    )
    charge_item = DeviceDefinitionChargeItemSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDefinition
        exclude = ["created_at", "updated_at"]
