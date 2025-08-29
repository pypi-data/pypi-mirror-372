"""Biologically Derived Products models."""

from django.db import models

from dfhir.base.models import (
    Attachment,
    BaseReference,
    CodeableConcept,
    Coding,
    Identifier,
    OrganizationReference,
    Period,
    Quantity,
    Range,
    Ratio,
    TimeStampedModel,
)
from dfhir.patients.models import PatientOrganizationReference
from dfhir.practitioners.models import PractitionerPractitionerRoleReference


class BiologicallyDerivedProductReference(BaseReference):
    """Biologically Derived Product Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="biologically_derived_product_reference_identifier",
        null=True,
    )
    biologically_derived_product = models.ForeignKey(
        "BiologicallyDerivedProduct",
        on_delete=models.CASCADE,
        related_name="biologically_derived_product_reference_biologically_derived_product",
        null=True,
    )


class BiologicallyDerivedProductCollection(TimeStampedModel):
    """Biologically Derived Product Collection model."""

    collector = models.ForeignKey(
        PractitionerPractitionerRoleReference,
        related_name="biologically_derived_product_collections_collector",
        on_delete=models.CASCADE,
        null=True,
    )
    source = models.ForeignKey(
        PatientOrganizationReference,
        related_name="biologically_derived_product_collections_source",
        on_delete=models.CASCADE,
        null=True,
    )
    collected_date_time = models.DateTimeField(null=True)
    collected_period = models.ForeignKey(
        Period,
        related_name="biologically_derived_product_collections_collected_period",
        on_delete=models.CASCADE,
        null=True,
    )
    procedure = models.ForeignKey(
        "procedures.Procedure",
        related_name="biologically_derived_product_collections_procedure",
        on_delete=models.CASCADE,
        null=True,
    )


class BiologicallyDerivedProductProperty(TimeStampedModel):
    """Biologically Derived Product Property model."""

    type = models.ForeignKey(
        CodeableConcept,
        related_name="biologically_derived_product_properties_type",
        on_delete=models.CASCADE,
        null=True,
    )
    value_boolean = models.BooleanField(null=True)
    value_integer = models.IntegerField(null=True)
    value_codeable_concept = models.ForeignKey(
        CodeableConcept,
        related_name="biologically_derived_product_properties_value_codeable_concept",
        on_delete=models.CASCADE,
        null=True,
    )
    value_period = models.ForeignKey(
        Period,
        related_name="biologically_derived_product_properties_value_period",
        on_delete=models.CASCADE,
        null=True,
    )
    value_quantity = models.ForeignKey(
        Quantity,
        related_name="biologically_derived_product_properties_value_quantity",
        on_delete=models.CASCADE,
        null=True,
    )
    value_range = models.ForeignKey(
        Range,
        related_name="biologically_derived_product_properties_value_range",
        on_delete=models.CASCADE,
        null=True,
    )
    value_ratio = models.ForeignKey(
        Ratio,
        related_name="biologically_derived_product_properties_value_ratio",
        on_delete=models.CASCADE,
        null=True,
    )
    value_string = models.CharField(max_length=255, null=True)
    value_attachment = models.ForeignKey(
        Attachment,
        related_name="biologically_derived_product_properties_value_attachment",
        on_delete=models.CASCADE,
        null=True,
    )


class BiologicallyDerivedProduct(TimeStampedModel):
    """Biologically Derived Product model."""

    product_category = models.ManyToManyField(
        CodeableConcept,
        related_name="biologically_derived_products_product_category",
        blank=True,
    )
    product_code = models.ForeignKey(
        CodeableConcept,
        related_name="biologically_derived_products_product_code",
        on_delete=models.CASCADE,
        null=True,
    )
    parent = models.ManyToManyField(
        BiologicallyDerivedProductReference,
        related_name="biologically_derived_products_parent",
        blank=True,
    )
    request = models.ManyToManyField(
        "servicerequests.ServiceRequestReference",
        related_name="biologically_derived_products_request",
        blank=True,
    )
    identifier = models.ManyToManyField(
        Identifier, related_name="biologically_derived_products_identifier", blank=True
    )
    biological_source_event = models.ForeignKey(
        Identifier,
        related_name="biologically_derived_products_biological_source_event",
        on_delete=models.CASCADE,
        null=True,
    )
    processing_facility = models.ManyToManyField(
        OrganizationReference,
        related_name="biologically_derived_products_processing_faciality",
        blank=True,
    )
    division = models.CharField(max_length=255, null=True)
    product_status = models.ForeignKey(
        Coding,
        related_name="biologically_derived_products_product_status",
        on_delete=models.CASCADE,
        null=True,
    )
    expiration_date = models.DateTimeField(null=True)
    collection = models.ForeignKey(
        BiologicallyDerivedProductCollection,
        related_name="biologically_derived_products_collection",
        on_delete=models.CASCADE,
        null=True,
    )
    storage_temp_requirements = models.ForeignKey(
        Range,
        related_name="biologically_derived_products_storage_temp_requirements",
        on_delete=models.CASCADE,
        null=True,
    )
    property = models.ManyToManyField(
        BiologicallyDerivedProductProperty,
        related_name="biologically_derived_products_property",
        blank=True,
    )
