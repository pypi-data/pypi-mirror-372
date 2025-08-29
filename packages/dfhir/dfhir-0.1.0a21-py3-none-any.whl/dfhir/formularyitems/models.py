"""formulary item models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    TimeStampedModel,
)
from dfhir.formularyitems.choices import FormularyItemStatusChoices


class FormularyItem(TimeStampedModel):
    """formulary item model."""

    identifier = models.ManyToManyField(
        Identifier, blank=True, related_name="formulary_item_identifier"
    )
    code = models.ForeignKey(
        CodeableConcept,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="formulary_item_code",
    )
    status = models.CharField(
        max_length=200, null=True, choices=FormularyItemStatusChoices.choices
    )


class FormularyItemReference(BaseReference):
    """formulary item reference model."""

    identifier = models.ForeignKey(
        Identifier,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="formulary_item_reference_identifier",
    )
    formulary_item = models.ForeignKey(
        FormularyItem,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name="formulary_item_reference_formulary_item",
    )
