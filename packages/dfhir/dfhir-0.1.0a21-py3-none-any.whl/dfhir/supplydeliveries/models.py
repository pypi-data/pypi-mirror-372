"""supply delivery models."""

from django.db import models

from dfhir.base.models import BaseReference, Identifier, TimeStampedModel
from dfhir.supplydeliveries.choices import SupplyDeliveryStatusChoices


class SupplyDeliveryContractReference(BaseReference):
    """supply delivery contract reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_contracts_reference_identifier",
    )
    supply_delivery = models.ForeignKey(
        "SupplyDelivery",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_contracts_supply_delivery",
    )
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_contracts_reference_contract",
    )


class SupplyDeliverReference(BaseReference):
    """supply delivery reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_reference_identifier",
    )
    supply_delivery = models.ForeignKey(
        "SupplyDelivery",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_reference_contract",
    )


class SupplyDeliverySuppliedItemItemReference(BaseReference):
    """supply delivery supplied item item reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_item_references_identifier",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_item_references_medication",
    )
    sustance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_item_references_substance",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_item_references_device",
    )
    biologically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_item_references_biologically_derived_product",
    )
    nutrition_product = models.ForeignKey(
        "nutritionproducts.NutritionProduct",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_item_references_nutrition_product",
    )
    inventory_item = models.ForeignKey(
        "inventoryitems.InventoryItem",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_item_references_inventory_item",
    )


class SupplyDeliverySupplierReference(BaseReference):
    """supply delivery supplier reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplier_references_identifier",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplier_references_organization",
    )

    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplier_references_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplier_references_practitioner_role",
    )


class SupplyDeliveryDestinationReference(BaseReference):
    """supply delivery destination reference."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_destination_references_identifier",
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_destination_references_location",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_destination_references_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_destination_references_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_destination_references_organization",
    )


class SupplyDeliveryReceiverReference(BaseReference):
    """supply delivery receiver reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_receiver_references_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_receiver_references_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_receiver_references_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_receiver_references_organization",
    )


class SupplyDeliverySuppliedItem(TimeStampedModel):
    """supply delivery supplied item class."""

    quantity = models.ForeignKey(
        "base.SimpleQuantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_quantity",
    )
    condition = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_condition",
    )
    item_codeable_concept = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_item_codealbe_concept",
    )
    item_reference = models.ForeignKey(
        SupplyDeliverySuppliedItemItemReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplied_item_item_reference",
    )


class SupplyDelivery(TimeStampedModel):
    """supply delivery model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="supply_delivery_identifier"
    )
    based_on = models.ManyToManyField(
        "supplyrequests.SupplyRequestReference",
        blank=True,
        related_name="supply_delivery_based_on",
    )
    part_of = models.ManyToManyField(
        SupplyDeliveryContractReference,
        blank=True,
        related_name="supply_delivery_part_of",
    )
    status = models.CharField(
        max_length=255, null=True, choices=SupplyDeliveryStatusChoices.choices
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_patient",
    )
    type = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_type",
    )
    stage = models.ForeignKey(
        "base.CodeableConcept",
        related_name="supply_delivery_stage",
        on_delete=models.DO_NOTHING,
        null=True,
    )

    supplied_item = models.ManyToManyField(
        SupplyDeliverySuppliedItem,
        blank=True,
        related_name="supply_delivery_supplied_item",
    )
    occurrence_date_time = models.DateTimeField(null=True, blank=True)
    occurrence_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_occurrence_period",
    )
    occurrence_timing = models.ForeignKey(
        "base.Timing",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_occurrence",
    )
    supplier = models.ForeignKey(
        SupplyDeliverySupplierReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_supplier",
    )
    destination = models.ForeignKey(
        SupplyDeliveryDestinationReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_delivery_destination",
    )
    receiver = models.ManyToManyField(
        SupplyDeliveryReceiverReference,
        blank=True,
        related_name="supply_delivery_receiver",
    )
