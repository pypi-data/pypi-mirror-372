"""biologically derived product dispenses models."""

from django.db import models

from dfhir.base.models import BaseReference, Identifier, TimeStampedModel
from dfhir.biologicallyderivedproductdispenses.choices import (
    BiologicallyDerivedProductDispenseStatus,
)


class BiologicallyDerivedProductDispenseReference(BaseReference):
    """biologically derived product dispenses reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_reference_identifier",
    )
    biologically_derived_product_dispense = models.ForeignKey(
        "BiologicallyDerivedProductDispense",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_reference_biologicallyderivedproductdispense",
    )


class BiologicallyDerivedProductDispensePerformer(TimeStampedModel):
    """biologically derived product dispenses performer model."""

    function = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_performer_function",
    )
    actor = models.ForeignKey(
        "practitioners.PractitionerReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_performer_actor",
    )


class BiologicallyDerivedProductDispense(TimeStampedModel):
    """Biologicallyderivedproductdispense models."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="biologicallyderivedproductdispense_identifier",
        blank=True,
    )
    based_on = models.ManyToManyField(
        "servicerequests.ServiceRequestReference",
        blank=True,
        related_name="biologicallyderivedproductdispense_based_on",
    )
    part_of = models.ManyToManyField(
        BiologicallyDerivedProductDispenseReference,
        blank=True,
        related_name="biologicallyderivedproductdispense_part_of",
    )
    status = models.CharField(
        max_length=255,
        null=True,
        choices=BiologicallyDerivedProductDispenseStatus.choices,
    )
    original_relationship_type = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_original_relationship_type",
    )
    product = models.ForeignKey(
        BiologicallyDerivedProductDispenseReference,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_product",
    )
    patient = models.ForeignKey(
        "patients.PatientReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_patient",
    )
    match_status = models.ForeignKey(
        "base.CodeableConcept",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_match_status",
    )
    performer = models.ManyToManyField(
        BiologicallyDerivedProductDispensePerformer,
        blank=True,
        related_name="biologicallyderivedproductdispense_performer",
    )
    location = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_location",
    )
    quantity = models.ForeignKey(
        "base.SimpleQuantity",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_quantity",
    )
    prepared_date = models.DateTimeField(null=True)
    when_handed_over = models.DateTimeField(null=True)
    destination = models.ForeignKey(
        "locations.LocationReference",
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="biologicallyderivedproductdispense_destination",
    )
    note = models.ManyToManyField(
        "base.Annotation",
        blank=True,
        related_name="biologicallyderivedproductdispense_note",
    )
    usage_instruction = models.CharField(max_length=255, null=True)
