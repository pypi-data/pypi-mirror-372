"""Payment Notices models."""

from django.db import models

from dfhir.base.models import (
    BaseReference,
    CodeableConcept,
    Identifier,
    Money,
    OrganizationReference,
    TimeStampedModel,
)

from . import choices


class PaymentNoticeReporterReference(BaseReference):
    """Payment Notice Reporter Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="payment_notice_reporter_reference",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="payment_notice_reporter_reference",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="payment_notice_reporter_reference",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="payment_notice_reporter_reference",
        null=True,
    )


class PaymentNoticePayeeReference(BaseReference):
    """Payment Notice Payee Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="payment_notice_payee_reference",
        null=True,
    )
    practitioner = models.ForeignKey(
        "practitioners.Practitioner",
        on_delete=models.CASCADE,
        related_name="payment_notice_payee_reference",
        null=True,
    )
    practitioner_role = models.ForeignKey(
        "practitionerroles.PractitionerRole",
        on_delete=models.CASCADE,
        related_name="payment_notice_payee_reference",
        null=True,
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="payment_notice_payee_reference",
        null=True,
    )


class PaymentNoticeRequestReference(BaseReference):
    """Payment Notice Request Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="payment_notice_request_reference",
        null=True,
    )
    claim = models.ForeignKey(
        "claims.Claim",
        on_delete=models.CASCADE,
        related_name="payment_notice_request_reference",
        null=True,
    )


class PaymentNoticeResponseReference(BaseReference):
    """Payment Notice Response Reference model."""

    identifier = models.ForeignKey(
        Identifier,
        on_delete=models.CASCADE,
        related_name="payment_notice_response_reference",
        null=True,
    )
    claim_response = models.ForeignKey(
        "claimresponses.ClaimResponse",
        on_delete=models.CASCADE,
        related_name="payment_notice_response_reference",
        null=True,
    )


class PaymentNotice(TimeStampedModel):
    """Payment Notice model."""

    identifier = models.ManyToManyField(
        Identifier,
        related_name="payment_notice",
        blank=True,
    )
    status = models.CharField(
        max_length=50,
        choices=choices.PaymentNoticeStatus.choices,
        default=choices.PaymentNoticeStatus.ACTIVE,
    )
    request = models.ForeignKey(
        PaymentNoticeRequestReference,
        on_delete=models.CASCADE,
        related_name="payment_notice",
        null=True,
    )
    response = models.ForeignKey(
        PaymentNoticeResponseReference,
        on_delete=models.CASCADE,
        related_name="payment_notice",
        null=True,
    )
    created = models.DateTimeField(auto_created=True, null=True)
    reporter = models.ForeignKey(
        PaymentNoticeReporterReference,
        on_delete=models.CASCADE,
        related_name="payment_notice",
        null=True,
    )
    payment = models.ForeignKey(
        "paymentreconciliations.PaymentReconciliation",
        on_delete=models.CASCADE,
        related_name="payment_notice",
        null=True,
    )
    payment_date = models.DateTimeField(null=True)
    payee = models.ForeignKey(
        PaymentNoticePayeeReference,
        on_delete=models.CASCADE,
        related_name="payment_notice",
        null=True,
    )
    recipient = models.ForeignKey(
        OrganizationReference,
        on_delete=models.CASCADE,
        related_name="payment_notice",
        null=True,
    )
    amount = models.ForeignKey(
        Money,
        on_delete=models.CASCADE,
        related_name="payment_notice",
        null=True,
    )
    payment_status = models.ForeignKey(
        CodeableConcept,
        on_delete=models.CASCADE,
        related_name="payment_notice",
        null=True,
    )
