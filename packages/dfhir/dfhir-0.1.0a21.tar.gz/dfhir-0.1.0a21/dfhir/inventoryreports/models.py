"""inventory report models."""

from django.db import models

from dfhir.base.models import BaseReference, Identifier, TimeStampedModel
from dfhir.biologicallyderivedproducts.models import BiologicallyDerivedProduct
from dfhir.devices.models import Device
from dfhir.inventoryreports.choices import (
    InventoryReportCountTypeChoices,
    InventoryReportStatusChoices,
)
from dfhir.medications.models import Medication
from dfhir.nutritionproducts.models import NutritionProduct


class InventoryReportInventoryListingItemItemReference(BaseReference):
    """inventory report inventory listing item reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_inventory_listing_item_reference_identifier",
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_inventory_listing_item_medication",
    )
    device = models.ForeignKey(
        Device,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_inventory_listing_item_device",
    )
    nutrition_product = models.ForeignKey(
        NutritionProduct,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_inventory_listing_item_nutrition_product",
    )
    inventory_item = models.ForeignKey(
        "inventoryitems.InventoryItem",
        null=True,
        related_name="inventory_report_inventory_listing_item_inventory_item",
        on_delete=models.DO_NOTHING,
    )
    biologically_derived_product = models.ForeignKey(
        BiologicallyDerivedProduct,
        on_delete=models.DO_NOTHING,
        related_name="inventory_report_inventory_listing_item_biologically_derived_product",
    )


class InventoryReportInventoryListingItemItemCodeableReference(TimeStampedModel):
    """inventory report inventory listing item codeable reference."""

    concept = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_inventory_listing_item_item_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        InventoryReportInventoryListingItemItemReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_inventory_listing_item_item_codeable_reference_reference",
    )


class InventoryReportInventoryListingItem(TimeStampedModel):
    """inventory report inventory listing item."""

    category = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_inventory_listing_item_category",
    )
    quality = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_inventory_listing_item_quality",
    )
    item = models.ManyToManyField(
        InventoryReportInventoryListingItemItemReference,
        blank=True,
        related_name="inventory_report_inventory_listing_item",
    )


class InventoryReportInventoryListing(TimeStampedModel):
    """inventory report inventory listing model."""

    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_inventory_listing",
    )
    item_status = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_inventory_listing_item_status",
    )
    counting_date_time = models.DateTimeField(null=True)
    item = models.ManyToManyField(
        InventoryReportInventoryListingItemItemCodeableReference,
        blank=True,
        related_name="inventory_report_inventory_listing",
    )


class InventoryReportReporterReference(BaseReference):
    """inventory report reporter reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_reporter_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_reporter_reference_practitioner",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_reporter_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_reporter_reference_related_person",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_reporter_reference_device",
    )


class InventoryReport(TimeStampedModel):
    """inventory report model."""

    identifier = models.ManyToManyField(
        Identifier, related_name="inventory_report", blank=True
    )
    status = models.CharField(
        max_length=255, null=True, choices=InventoryReportStatusChoices.choices
    )
    count_type = models.CharField(
        max_length=255, null=True, choices=InventoryReportCountTypeChoices.choices
    )
    operation_type = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_operational_type",
    )
    operation_type_reason = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report_operational_reason",
    )
    reported_date_time = models.DateTimeField(null=True)
    reporter = models.ForeignKey(
        InventoryReportReporterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report",
    )
    reporting_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="inventory_report",
    )
    inventory_listing = models.ManyToManyField(
        InventoryReportInventoryListing, related_name="inventory_report", blank=True
    )
    note = models.ManyToManyField(
        "base.Annotation", blank=True, related_name="inventory_report"
    )
