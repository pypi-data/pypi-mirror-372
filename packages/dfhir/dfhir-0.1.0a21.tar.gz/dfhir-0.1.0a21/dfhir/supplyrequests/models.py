"""supply requests models."""

from django.db import models

from dfhir.base.models import BaseReference, Identifier, TimeStampedModel
from dfhir.supplyrequests.choices import (
    SupplyRequestIntentChoices,
    SupplyRequestPriorityChoices,
    SupplyRequestStatusChoices,
)


class SupplyRequestParameter(TimeStampedModel):
    """supply request parameter model."""

    code = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        related_name="supply_request_parameter_code",
        null=True,
    )
    value_codeable_concept = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        related_name="supply_request_parameter_value_codeable_concept",
    )
    value_quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        related_name="supply_request_parameter_value_quantity",
        null=True,
    )
    value_range = models.ForeignKey(
        "base.Range",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_parameter_value_range",
    )
    value_boolean = models.BooleanField(null=True)


class SupplyRequestRequesterReference(BaseReference):
    """supply request requester reference model."""

    identifier = models.ForeignKey(
        "base.Identifier",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_requester_reference_identifier",
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_requester_reference_practitioner",
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_reques_requestert_reference_practitioner_role",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_requester_reference_organization",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_requester_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_requester_reference_related_person",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_requester_reference_device",
    )
    care_team = models.ForeignKey(
        "careteams.CareTeam",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_requester_reference_care_team",
    )


class SupplyRequestSupplierReference(BaseReference):
    """supply request supplier reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_supplier_reference_identifier",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_supplier_reference_organization",
    )
    healthcare_service = models.ForeignKey(
        "healthcareservices.HealthcareService",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_supplier_reference_healthcare_service",
    )


class SupplyRequestReasonReference(BaseReference):
    """supply request reason reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_reason_reference_identifier",
    )
    condition = models.ForeignKey(
        "conditions.Condition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_reason_reference_condition",
    )
    observation = models.ForeignKey(
        "observations.Observation",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_reason_reference_observation",
    )
    diagnostic_report = models.ForeignKey(
        "diagnosticreports.DiagnosticReport",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_reason_reference_diagnostic_report",
    )
    document_reference = models.ForeignKey(
        "documentreferences.DocumentReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_reason_reference_document_reference",
    )


class SupplyRequestReasonCodeableReference(TimeStampedModel):
    """supply request reason codeable reference model."""

    concept = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_reason_codeable_reference_concept",
    )
    reference = models.ForeignKey(
        SupplyRequestReasonReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_reason_codeable_reference_reference",
    )


class SupplyRequestDeliverFromReference(BaseReference):
    """supply request deliver from reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_from_reference_identifier",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_from_reference_organization",
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_from_reference_location",
    )


class SupplyRequestDeliverToReference(BaseReference):
    """supply request deliver to reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_to_reference_identifier",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_to_reference_organization",
    )
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_to_reference_location",
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_to_reference_patient",
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_to_reference_related_person",
    )


class SupplyRequestItemReference(BaseReference):
    """supply request reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_item_reference_identifier",
    )
    medication = models.ForeignKey(
        "medications.Medication",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_item_reference_medication",
    )
    substance = models.ForeignKey(
        "substances.Substance",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_item_reference_substance",
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_item_reference_device",
    )
    device_definition = models.ForeignKey(
        "devicedefinitions.DeviceDefinition",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_item_reference_device_definition",
    )
    biologically_derived_product = models.ForeignKey(
        "biologicallyderivedproducts.BiologicallyDerivedProduct",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_item_reference_biologically_derived_product",
    )
    nutrition_product = models.ForeignKey(
        "nutritionproducts.NutritionProduct",
        on_delete=models.DO_NOTHING,
        related_name="supply_request_item_reference_nutrition_order",
        null=True,
    )
    inventory_item = models.ForeignKey(
        "inventoryitems.InventoryItem",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_item_reference_inventory_item",
    )


class SupplyRequestItemCodeableReference(TimeStampedModel):
    """supply request item codeable reference model."""

    concept = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        related_name="supply_request_item_codeable_reference_concept",
        null=True,
    )
    reference = models.ForeignKey(
        SupplyRequestItemReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_item_codeable_reference_reference",
    )


class SupplyRequest(TimeStampedModel):
    """supply request model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="supply_request_identifier"
    )
    status = models.CharField(
        max_length=200, null=True, choices=SupplyRequestStatusChoices.choices
    )
    intent = models.CharField(
        max_length=255, null=True, choices=SupplyRequestIntentChoices.choices
    )
    based_on = models.ManyToManyField(
        "base.Reference", related_name="supply_request_based_on", blank=True
    )
    category = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_category",
    )
    priority = models.CharField(
        max_length=255, null=True, choices=SupplyRequestPriorityChoices.choices
    )
    deliver_for = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_for",
    )
    item = models.ForeignKey(
        SupplyRequestItemCodeableReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_item",
    )
    quantity = models.ForeignKey(
        "base.Quantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_quantity",
    )
    parameter = models.ManyToManyField(
        SupplyRequestParameter, blank=True, related_name="supply_request_parameter"
    )
    occurrence_date_time = models.DateTimeField(null=True, blank=True)
    occurrence_period = models.ForeignKey(
        "base.Period",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_occurrence_period",
    )
    occurrence_timing = models.ForeignKey(
        "base.Timing",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_occurrence_timing",
    )
    authored_on = models.DateTimeField(null=True, blank=True)
    requester = models.ForeignKey(
        SupplyRequestRequesterReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_requester",
    )
    supplier = models.ManyToManyField(
        SupplyRequestSupplierReference,
        blank=True,
        related_name="supply_request_supplier",
    )
    reason = models.ManyToManyField(
        SupplyRequestReasonCodeableReference,
        blank=True,
        related_name="supply_request_reason",
    )
    deliver_from = models.ForeignKey(
        SupplyRequestDeliverFromReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_from",
    )
    deliver_to = models.ForeignKey(
        SupplyRequestDeliverToReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_deliver_to",
    )


class SupplyRequestReference(BaseReference):
    """supply request reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=False,
        related_name="supply_request_reference_identifier",
    )
    supply_request = models.ForeignKey(
        SupplyRequest,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="supply_request_reference_supply_request",
    )
