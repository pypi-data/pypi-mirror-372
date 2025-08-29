"""inventory item models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)
from dfhir.base.models import Quantity as Duration
from dfhir.inventoryitems.choices import (
    InventoryItemNameLanguageChoices,
    InventoryItemNameTypeChoices,
    InventoryItemStatusChoices,
)
from dfhir.patients.models import PatientOrganizationReference


class InventoryItemAssociationTypeReference(BaseReference):
    """inventory item association type reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="association_type_reference_identifiers",
    )
    inventor_item = models.ForeignKey(
        "inventoryitems.InventoryItem",
        on_delete=models.SET_NULL,
        null=True,
        related_name="association_type_reference_inventory_items",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.SET_NULL,
        null=True,
        related_name="association_type_reference_medications",
    )
    medication_knowledge = models.ForeignKey(
        "medicationknowledges.MedicationKnowledge",
        on_delete=models.SET_NULL,
        null=True,
        related_name="association_type_reference_medication_knowledge",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        related_name="association_type_reference_devices",
    )
    device_definition = models.ForeignKey(
        "devicedefinitions.DeviceDefinition",
        on_delete=models.SET_NULL,
        null=True,
        related_name="association_type_reference_device_definitions",
    )
    nutrition_product = models.ForeignKey(
        "nutritionproducts.NutritionProduct",
        on_delete=models.SET_NULL,
        null=True,
        related_name="association_type_reference_nutrition_products",
    )
    biological_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.SET_NULL,
        null=True,
        related_name="association_type_reference_biological_derived_products",
    )


class InventoryItemName(TimeStampedModel):
    """inventory item name model."""

    name_type = models.CharField(
        max_length=255, null=True, choices=InventoryItemNameTypeChoices.choices
    )
    language = models.CharField(
        max_length=255, null=True, choices=InventoryItemNameLanguageChoices.choices
    )
    name = models.CharField(max_length=255, null=True)


class InventoryItemResponsibleOrganization(TimeStampedModel):
    """inventory item responsible organization model."""

    code = models.ForeignKey(
        CodeableConcept,
        null=True,
        on_delete=models.CASCADE,
        related_name="inventory_item_responsible_organization_codes",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_responsible_organization_organizations",
    )


class InventoryItemDescription(TimeStampedModel):
    """inventory item description model."""

    language = models.CharField(
        max_length=255, null=True, choices=InventoryItemNameLanguageChoices.choices
    )
    description = models.TextField(null=True)


class InventoryItemAssociation(TimeStampedModel):
    """inventory item association model."""

    association_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="inventory_item_associations_association_types",
    )
    related_item = models.ForeignKey(
        InventoryItemAssociationTypeReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_associations_related_items",
    )
    quantity = models.ForeignKey(
        "base.Ratio",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_associations_quantity",
    )


class InventoryItemCharacteristic(TimeStampedModel):
    """inventory item characteristic model."""

    characteristic_type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_characteristics_characteristic_types",
    )
    value_string = models.CharField(max_length=255, null=True)
    value_integer = models.IntegerField(null=True)
    value_decimal = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    value_boolean = models.BooleanField(null=True)
    value_url = models.URLField(null=True)
    value_date_time = models.DateTimeField(null=True)
    value_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_characteristics_value_quantities",
    )
    value_range = models.ForeignKey(
        "base.Range",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_characteristics_value_ranges",
    )
    value_ratio = models.ForeignKey(
        "base.Ratio",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_characteristics_value_ratios",
    )
    value_annotation = models.ForeignKey(
        "base.Annotation",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_characteristics_value_annotations",
    )
    value_duration = models.ForeignKey(
        Duration,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_characteristics_value_durations",
    )
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_characteristics_value_codeable_concepts",
    )


class InventoryItemInstance(TimeStampedModel):
    """inventory item instance model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="inventory_item_instances", blank=True
    )
    lot_number = models.CharField(max_length=255, null=True)
    expiry = models.DateTimeField(null=True)
    subject = models.ForeignKey(
        PatientOrganizationReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_instances_subjects",
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_instances_locations",
    )


class InventoryItemProductReference(BaseReference):
    """inventory item product reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_product_reference_identifiers",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_product_reference_medications",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_product_reference_devices",
    )
    nutrition_product = models.ForeignKey(
        "nutritionproducts.NutritionProduct",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_product_references_nutrition_product",
    )
    biologically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_product_references_biologicallyderived_product",
    )


class InventoryItem(TimeStampedModel):
    """inventory item model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="inventory_items_identifier", blank=True
    )
    status = models.CharField(
        max_length=255, null=True, choices=InventoryItemStatusChoices.choices
    )
    category = models.ManyToManyField(
        CodeableConcept, related_name="inventory_items_categories", blank=True
    )
    code = models.ManyToManyField(
        CodeableConcept, related_name="inventory_items_codes", blank=True
    )
    name = models.ManyToManyField(
        InventoryItemName, related_name="inventory_items_names", blank=True
    )
    responsible_organization = models.ManyToManyField(
        InventoryItemResponsibleOrganization,
        related_name="inventory_items_responsible_organizations",
        blank=True,
    )
    description = models.ForeignKey(
        InventoryItemDescription,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_items_descriptions",
    )
    inventory_status = models.ManyToManyField(
        CodeableConcept, related_name="inventory_items_inventory_statuses", blank=True
    )
    base_unit = models.ForeignKey(
        CodeableConcept,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_items_base_units",
    )
    net_content = models.ForeignKey(
        "base.Quantity",
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_items_net_contents",
    )
    association = models.ManyToManyField(
        InventoryItemAssociation,
        related_name="inventory_items_associations",
        blank=True,
    )
    characteristic = models.ManyToManyField(
        InventoryItemCharacteristic,
        related_name="inventory_items_characteristics",
        blank=True,
    )
    instance = models.ForeignKey(
        InventoryItemInstance,
        null=True,
        on_delete=models.SET_NULL,
        related_name="inventory_items_insurances",
    )
    product_reference = models.ForeignKey(
        InventoryItemProductReference,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_items_product_references",
    )


class InventoryItemReference(BaseReference):
    """inventory item reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_references_identifiers",
    )
    inventory_item = models.ForeignKey(
        InventoryItem,
        on_delete=models.SET_NULL,
        null=True,
        related_name="inventory_item_references_inventory_items",
    )
