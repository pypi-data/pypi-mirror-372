"""payment reconciliation serializers."""

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.accounts.serializers import AccountReferenceSerializer
from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    MoneySerializer,
    PeriodSerializer,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.paymentreconciliations.models import (
    OrganizationPractitionerPractitionerRoleReference,
    PaymentReconciliation,
    PaymentReconciliationAllocation,
    PaymentReconciliationAllocationTargetReference,
    PaymentReconciliationPaymentIssuerReference,
    PaymentReconciliationProcessNote,
    PaymentReconciliationReference,
)
from dfhir.practitionerroles.serializers import PractitionerRoleReferenceSerializer
from dfhir.tasks.serializers import TaskReferenceSerializer


class OrganizationPractitionerPractitionerRoleReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Organization Practitioner Practitioner Role Reference Serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = OrganizationPractitionerPractitionerRoleReference
        exclude = ["created_at", "updated_at"]


class PaymentReconciliationAllocationTargetReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Payment Reconciliation Allocation Target Reference Serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = PaymentReconciliationAllocationTargetReference
        exclude = ["created_at", "updated_at"]


class PaymentReconciliationPaymentIssuerReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Payment Reconciliation Payment Issuer Reference Serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = PaymentReconciliationPaymentIssuerReference
        exclude = ["created_at", "updated_at"]


class PaymentReconciliationAllocationSerializer(WritableNestedModelSerializer):
    """Payment Reconciliation Allocation Serializer."""

    identifier = IdentifierSerializer(many=False, required=False)
    predecessor = IdentifierSerializer(many=False, required=False)
    target = PaymentReconciliationAllocationTargetReferenceSerializer(
        many=False, required=False
    )
    target_item_identifier = IdentifierSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    account = AccountReferenceSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    submitter = OrganizationPractitionerPractitionerRoleReferenceSerializer(
        many=False, required=False
    )
    responsible = PractitionerRoleReferenceSerializer(required=False)
    payee = OrganizationPractitionerPractitionerRoleReferenceSerializer(
        many=False, required=False
    )
    amount = MoneySerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = PaymentReconciliationAllocation
        exclude = ["created_at", "updated_at"]


class PaymentReconciliationProcessNoteSerializer(serializers.ModelSerializer):
    """payment reconciliation process note serializer."""

    class Meta:
        """Meta options."""

        model = PaymentReconciliationProcessNote
        exclude = ["created_at", "updated_at"]


class PaymentReconciliationSerializer(WritableNestedModelSerializer):
    """Payment Reconciliation Process Note Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    kind = CodeableConceptSerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)
    enterer = OrganizationPractitionerPractitionerRoleReferenceSerializer(
        required=False
    )
    issuer_type = CodeableConceptSerializer(many=False, required=False)
    payment_issuer = PaymentReconciliationPaymentIssuerReferenceSerializer(
        many=False, required=False
    )
    request = TaskReferenceSerializer(required=False)
    requestor = OrganizationPractitionerPractitionerRoleReferenceSerializer(  # codespell:ignore requestor
        required=False
    )
    location = LocationReferenceSerializer(many=False, required=False)
    method = CodeableConceptSerializer(many=False, required=False)
    tendered_amount = MoneySerializer(many=False, required=False)
    returned_amount = MoneySerializer(many=False, required=False)
    amount = MoneySerializer(many=False, required=False)
    payment_identifier = IdentifierSerializer(many=False, required=False)
    allocation = PaymentReconciliationAllocationSerializer(many=True, required=False)
    form_code = CodeableConceptSerializer(required=False)
    process_note = PaymentReconciliationProcessNoteSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = PaymentReconciliation
        exclude = ["created_at", "updated_at"]


class PaymentReconciliationReferenceSerializer(BaseReferenceModelSerializer):
    """Payment Reconciliation Reference Serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = PaymentReconciliationReference
        exclude = ["created_at", "updated_at"]
