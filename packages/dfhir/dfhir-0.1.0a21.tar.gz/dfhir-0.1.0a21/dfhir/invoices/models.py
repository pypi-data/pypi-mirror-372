"""Invoice models."""

from django.db import models

from dfhir.base.models import (
    Annotation,
    BaseReference,
    CodeableConcept,
    Identifier,
    MonetaryComponent,
    Money,
    OrganizationReference,
    Period,
    TimeStampedModel,
)

from . import choices


class InvoiceRecipientReference(BaseReference):
    """Invoice recipient reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="invoice_recipient_reference_identifier",
        null=True,
    )
    organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="invoice_recipient_reference_organization",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="invoice_recipient_reference_patient",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="invoice_recipient_reference_related_person",
        null=True,
    )


class InvoiceParticipantActorReference(BaseReference):
    """Invoice participant actor reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="invoice_participant_actor_reference_identifier",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="invoice_participant_actor_reference_practitioner",
        null=True,
    )
    organization = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="invoice_participant_actor_reference_organization",
        null=True,
    )
    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="invoice_participant_actor_reference_patient",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="invoice_participant_actor_reference_practitioner_role",
        null=True,
    )
    device = models.ForeignKey(
        "devices.Device",
        on_delete=models.CASCADE,
        related_name="invoice_participant_actor_reference_device",
        null=True,
    )
    related_person = models.ForeignKey(
        "relatedpersons.RelatedPerson",
        on_delete=models.CASCADE,
        related_name="invoice_participant_actor_reference_related_person",
        null=True,
    )


class InvoiceParticipant(TimeStampedModel):
    """Invoice participant model."""

    role = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="invoice_participant_role",
        null=True,
    )
    actor = models.ForeignKey(
        InvoiceParticipantActorReference,
        on_delete=models.CASCADE,
        related_name="invoice_participant_actor",
        null=True,
    )


class InvoiceLineItem(TimeStampedModel):
    """Invoice line item model."""

    sequence = models.PositiveIntegerField(null=True)
    service_date = models.DateField(null=True)
    service_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="invoice_line_item_service_period",
        null=True,
    )
    charge_item_reference = models.ForeignKey(
        "chargeitems.ChargeItemReference",
        on_delete=models.CASCADE,
        related_name="invoice_line_item_charge_item_reference",
        null=True,
    )
    charge_item_codeable_concept = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="invoice_line_item_charge_item_codeable_concept",
        null=True,
    )
    price_component = models.ManyToManyField(
        MonetaryComponent,
        related_name="invoice_line_item_price_component",
        blank=True,
    )


class Invoice(TimeStampedModel):
    """Invoice model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="invoice_identifier",
        blank=True,
    )
    status = models.CharField(
        max_length=255,
        choices=choices.InvoiceStatus.choices,
        default=choices.InvoiceStatus.DRAFT,
    )
    cancelled_reason = models.TextField(null=True)
    type = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="invoice_type",
        null=True,
    )
    subject = models.ForeignKey(
        "patients.PatientGroupReference",
        on_delete=models.CASCADE,
        related_name="invoice_subject",
        null=True,
    )
    recipient = models.ForeignKey(
        InvoiceRecipientReference,
        on_delete=models.CASCADE,
        related_name="invoice_recipient",
        null=True,
    )
    date = models.DateTimeField(null=True)
    creation = models.DateTimeField(null=True)
    period_date = models.DateField(null=True)
    period_period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name="invoice_period_period",
        null=True,
    )
    participant = models.ManyToManyField(
        InvoiceParticipant,
        related_name="invoice_participant",
        blank=True,
    )
    issuer = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="invoice_issuer",
        null=True,
    )
    account = models.ForeignKey(
        "accounts.AccountReference",
        on_delete=models.CASCADE,
        related_name="invoice_account",
        null=True,
    )
    line_item = models.ManyToManyField(
        InvoiceLineItem,
        related_name="invoice_line_item",
        blank=True,
    )
    total_price_component = models.ManyToManyField(
        MonetaryComponent,
        related_name="invoice_total_price_component",
        blank=True,
    )
    total_net = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="invoice_total_net",
        null=True,
    )
    total_gross = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="invoice_total_gross",
        null=True,
    )
    payment_terms = models.TextField(null=True)
    note = models.ManyToManyField(
        Annotation,
        related_name="invoice_note",
        blank=True,
    )


class InvoiceReference(BaseReference):
    """Invoice reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="invoice_reference_identifier",
        null=True,
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="invoice_reference_invoice",
        null=True,
    )
