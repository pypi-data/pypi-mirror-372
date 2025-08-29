"""Device definition models."""

from django.db import models

from dfhir.base.models import (
    Attachment,
    BaseReference,
    CodeableConcept,
    Coding,
    ContactDetail,
    Identifier,
    OrganizationReference,
    Period,
    ProductShelfLife,
    Quantity,
    Range,
    RelatedArtifact,
    TimeStampedModel,
    UsageContext,
)

from . import choices


class DeviceDefinitionMarketDistribution(TimeStampedModel):
    """DeviceDefinitionMarketDistribution model."""

    market_period = models.ForeignKey(Period, on_delete=models.CASCADE, null=True)
    sub_jurisdiction = models.CharField(max_length=255, null=True)


class DeviceDefinitionUdiDeviceIdentifier(TimeStampedModel):
    """DeviceDefinitionUdiDeviceIdentifier model."""

    device_identifier = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    jurisdiction = models.CharField(max_length=255)
    market_distribution = models.ManyToManyField(
        DeviceDefinitionMarketDistribution, blank=True
    )


class DeviceDefinitionRegulatoryIdentifier(TimeStampedModel):
    """DeviceDefinitionRegulatoryIdentifier model."""

    type = models.CharField(
        max_length=255, choices=choices.DeviceDefinitionRegulatoryIdentifierType.choices
    )
    device_identifier = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    jurisdiction = models.CharField(max_length=255)


class DeviceDefinitionDeviceName(TimeStampedModel):
    """DeviceDefinitionDeviceName model."""

    name = models.CharField(max_length=255)
    type = models.ForeignKey(
        CodeableConcept,
        related_name="device_definition_device_name_type",
        on_delete=models.CASCADE,
        null=True,
    )


class DeviceDefinitionClassification(TimeStampedModel):
    """DeviceDefinitionClassification model."""

    type = models.ForeignKey(
        CodeableConcept,
        related_name="device_definition_classification_type",
        on_delete=models.CASCADE,
        null=True,
    )
    justification = models.ManyToManyField(
        RelatedArtifact,
        related_name="device_definition_classification_jurisdication",
        blank=True,
    )


class DeviceDefinitionConformsTo(TimeStampedModel):
    """DeviceDefinitionConformsTo model."""

    category = models.ForeignKey(
        CodeableConcept,
        related_name="device_definition_conforms_to_category",
        on_delete=models.CASCADE,
        null=True,
    )
    specification = models.ForeignKey(
        CodeableConcept,
        related_name="device_definition_conforms_to_specification",
        on_delete=models.CASCADE,
        null=True,
    )
    version = models.CharField(max_length=255, null=True)
    source = models.ManyToManyField(
        RelatedArtifact, related_name="device_definition_conforms_to_source", blank=True
    )


class DeviceDefinitionHasPart(TimeStampedModel):
    """DeviceDefinitionHasPart model."""

    reference = models.ForeignKey(
        "DeviceDefinitionReference",
        related_name="device_definition_has_part_reference",
        on_delete=models.CASCADE,
        null=True,
    )
    count = models.IntegerField(null=True)


class DeviceDefinitionReference(BaseReference):
    """Device definition reference."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="device_definition_reference_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    device_definition = models.ForeignKey(
        "DeviceDefinition",
        related_name="device_definition_reference_device_definition",
        on_delete=models.CASCADE,
        null=True,
    )


class DeviceDefinitionCodeableReference(TimeStampedModel):
    """DeviceDefinitionCodeableReference model."""

    reference = models.ForeignKey(
        DeviceDefinitionReference,
        related_name="device_definition_codeable_reference_reference",
        on_delete=models.CASCADE,
        null=True,
    )
    concept = models.ForeignKey(
        CodeableConcept,
        related_name="device_definition_codeable_reference_concept",
        on_delete=models.CASCADE,
        null=True,
    )


class DeviceDefinitionPackagingDistributor(TimeStampedModel):
    """Device definition packaging distributor model."""

    name = models.CharField(max_length=255)
    organization_reference = models.ForeignKey(
        OrganizationReference,
        related_name="device_definition_packaging_distributor_organization_reference",
        on_delete=models.CASCADE,
        null=True,
    )


class DeviceDefinitionPackaging(TimeStampedModel):
    """Device definition packaging model."""

    identifier = models.ForeignKey(
        Identifier,
        related_name="device_definition_packaging_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    type = models.ForeignKey(
        CodeableConcept,
        related_name="device_definition_packaging_type",
        on_delete=models.CASCADE,
        null=True,
    )
    count = models.IntegerField(null=True)
    distributor = models.ManyToManyField(
        DeviceDefinitionPackagingDistributor,
        related_name="device_definition_packaging_distributor",
        blank=True,
    )
    udi_device_identifier = models.ManyToManyField(
        DeviceDefinitionUdiDeviceIdentifier,
        related_name="device_definition_packaging_udihistory",
        blank=True,
    )
    packaging = models.ForeignKey(
        "self",
        related_name="device_definition_packaging_packaging",
        on_delete=models.CASCADE,
        null=True,
    )


class DeviceDefinitionDeviceVersion(TimeStampedModel):
    """DeviceVersion model."""

    type = models.ForeignKey(
        CodeableConcept,
        related_name="device_definition_device_version_type",
        on_delete=models.CASCADE,
        null=True,
    )
    component = models.ForeignKey(
        Identifier,
        related_name="device_definition_device_version_component",
        on_delete=models.CASCADE,
        null=True,
    )
    value = models.CharField(max_length=255, null=True)


class DeviceDefinitionProperty(TimeStampedModel):
    """DeviceDefinitionProperty model."""

    type = models.ForeignKey(
        CodeableConcept,
        related_name="device_definition_property_type",
        on_delete=models.CASCADE,
        null=True,
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        related_name="device_definition_property_value_code",
        on_delete=models.CASCADE,
        null=True,
    )
    value_string = models.CharField(max_length=255, null=True)
    value_boolean = models.BooleanField(null=True)
    value_integer = models.IntegerField(null=True)
    value_quantity = models.ForeignKey(
        Quantity,
        related_name="device_definition_property_value_quantity",
        on_delete=models.CASCADE,
        null=True,
    )
    value_range = models.ForeignKey(
        Range,
        related_name="device_definition_property_value_range",
        on_delete=models.CASCADE,
        null=True,
    )
    value_attachment = models.ForeignKey(
        Attachment,
        related_name="device_definition_property_value_attachment",
        on_delete=models.CASCADE,
        null=True,
    )


class DeviceDefinitionLink(TimeStampedModel):
    """DeviceDefinitionLink model."""

    relation = models.ForeignKey(
        Coding,
        related_name="device_definition_link_relation",
        on_delete=models.CASCADE,
        null=True,
    )
    related_device = models.ForeignKey(
        "DeviceDefinitionCodeableReference",
        related_name="device_definition_link_related_device",
        on_delete=models.CASCADE,
        null=True,
    )


class DeviceDefinitionMaterial(TimeStampedModel):
    """DeviceDefinitionMaterial model."""

    substance = models.ForeignKey(
        CodeableConcept,
        related_name="device_definition_material_substance",
        on_delete=models.CASCADE,
        null=True,
    )
    alternate = models.BooleanField(null=True)
    allergenic_indicator = models.BooleanField(null=True)


class DeviceDefinitionGuideline(TimeStampedModel):
    """DeviceDefinitionGuideline model."""

    use_context = models.ManyToManyField(
        UsageContext, related_name="device_definition_guideline_use_context", blank=True
    )
    usage_instruction = models.TextField(null=True)
    related_artifact = models.ManyToManyField(
        RelatedArtifact,
        related_name="device_definition_guideline_related_artifact",
        blank=True,
    )
    indication = models.ManyToManyField(
        CodeableConcept,
        related_name="device_definition_guideline_indication",
        blank=True,
    )
    contraindication = models.ManyToManyField(
        CodeableConcept,
        related_name="device_definition_guideline_contraindication",
        blank=True,
    )
    warning = models.ManyToManyField(
        CodeableConcept, related_name="device_definition_guideline_warning", blank=True
    )
    intended_use = models.CharField(max_length=255, null=True)


class DeviceDefinitionCorrectiveAction(TimeStampedModel):
    """DeviceDefinitionCorrectiveAction model."""

    recall = models.BooleanField(null=True)
    scope = models.CharField(
        max_length=255,
        null=True,
        choices=choices.DeviceDefinitionCorrectiveActionScope.choices,
    )
    period = models.ForeignKey(
        Period,
        related_name="device_definition_corrective_action_period",
        on_delete=models.CASCADE,
        null=True,
    )


class DeviceDefinitionChargeItem(TimeStampedModel):
    """DeviceDefinitionChargeItem model."""

    # charge_item_code = models.ForeignKey(
    #     "chargeitems.ChargeItemDefinitionCodeableReference",
    #     related_name="device_definition_charge_item_charge_item_code",
    #     on_delete=models.CASCADE,
    #     null=True,
    # )
    count = models.ForeignKey(
        Quantity,
        related_name="device_definition_charge_item_count",
        on_delete=models.CASCADE,
        null=True,
    )
    effective_period = models.ForeignKey(
        Period,
        related_name="device_definition_charge_item_effective_period",
        on_delete=models.CASCADE,
        null=True,
    )
    use_context = models.ManyToManyField(
        UsageContext,
        related_name="device_definition_charge_item_use_context",
        blank=True,
    )


class DeviceDefinition(TimeStampedModel):
    """DeviceDefinition model."""

    description = models.TextField(null=True)
    identifier = models.ManyToManyField(
        Identifier, related_name="device_definitions_identifier", blank=True
    )
    udi_device_identifier = models.ForeignKey(
        DeviceDefinitionUdiDeviceIdentifier,
        related_name="device_definitions_udi_device_identifier",
        on_delete=models.CASCADE,
        null=True,
    )
    regulatory_identifier = models.ManyToManyField(
        DeviceDefinitionRegulatoryIdentifier, blank=True
    )
    part_number = models.CharField(max_length=255, null=True)
    manufacturer = models.ForeignKey(
        OrganizationReference,
        related_name="device_definitions_manufacturer",
        on_delete=models.CASCADE,
        null=True,
    )
    device_name = models.ManyToManyField(
        DeviceDefinitionDeviceName,
        related_name="device_definitions_device_name",
        blank=True,
    )
    model_number = models.CharField(max_length=255, null=True)
    contact = models.ManyToManyField(
        ContactDetail, related_name="device_definitions_contact", blank=True
    )
    publisher = models.CharField(max_length=255, null=True)
    classification = models.ManyToManyField(
        DeviceDefinitionClassification,
        related_name="device_definitions_classification",
        blank=True,
    )
    conforms_to = models.ManyToManyField(
        DeviceDefinitionConformsTo,
        related_name="device_definitions_conforms_to",
        blank=True,
    )
    has_part = models.ManyToManyField(
        DeviceDefinitionHasPart, related_name="device_definitions_has_part", blank=True
    )
    packaging = models.ManyToManyField(
        DeviceDefinitionPackaging,
        related_name="device_definitions_packaging",
        blank=True,
    )
    # device_version = models.ManyToManyField(
    #     DeviceDefinitionDeviceVersion, related_name="device_definitions_device_version", blank=True
    # )
    safety = models.ManyToManyField(
        CodeableConcept, related_name="device_definitions_safety", blank=True
    )
    shelf_life_storage = models.ForeignKey(
        ProductShelfLife,
        related_name="device_definitions_shelf_life_storage",
        on_delete=models.CASCADE,
        null=True,
    )
    language_code = models.ForeignKey(
        CodeableConcept,
        related_name="device_definitions_language_code",
        on_delete=models.CASCADE,
        null=True,
    )
    property = models.ManyToManyField(
        DeviceDefinitionProperty, related_name="device_definitions_property", blank=True
    )
    link = models.ManyToManyField(
        DeviceDefinitionLink, related_name="device_definitions_link", blank=True
    )
    material = models.ManyToManyField(
        DeviceDefinitionMaterial, related_name="device_definitions_material", blank=True
    )
    guideline = models.ForeignKey(
        DeviceDefinitionGuideline,
        related_name="device_definitions_guideline",
        on_delete=models.CASCADE,
        null=True,
    )
    corrective_action = models.ForeignKey(
        DeviceDefinitionCorrectiveAction,
        related_name="device_definitions_corrective_action",
        on_delete=models.CASCADE,
        null=True,
    )
    charge_item = models.ManyToManyField(
        DeviceDefinitionChargeItem,
        related_name="device_definitions_charge_item",
        blank=True,
    )
