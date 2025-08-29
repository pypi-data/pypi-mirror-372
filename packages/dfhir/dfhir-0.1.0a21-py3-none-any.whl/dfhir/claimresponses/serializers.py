"""Claim responses serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AddressSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    MoneySerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    QuantitySerializer,
    SimpleQuantitySerializer,
)
from dfhir.bodystructures.serializers import BodyStructureCodeableReferenceSerializer
from dfhir.claims.serializers import ClaimReferenceSerializer
from dfhir.coverages.serializers import CoverageReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer

from .models import (
    ClaimResponse,
    ClaimResponseAddItem,
    ClaimResponseAddItemBodySite,
    ClaimResponseAddItemDetail,
    ClaimResponseAddItemDetailSubDetail,
    ClaimResponseAddItemProviderReference,
    ClaimResponseAddItemRequestReference,
    ClaimResponseError,
    ClaimResponseEvent,
    ClaimResponseInsurance,
    ClaimResponseItem,
    ClaimResponseItemAdjudication,
    ClaimResponseItemDetail,
    ClaimResponseItemDetailSubDetail,
    ClaimResponseItemReviewOutcome,
    ClaimResponsePayment,
    ClaimResponseProcessNote,
    ClaimResponseReference,
    ClaimResponseRequestorReference,
    ClaimResponseTotal,
)


class ClaimResponseReferenceSerializer(BaseReferenceModelSerializer):
    """ClaimResponse reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseReference
        exclude = ["created_at", "updated_at"]


class ClaimResponseAddItemProviderReferenceReferenceSerializer(
    BaseReferenceModelSerializer
):
    """ClaimResponse Provider Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseAddItemProviderReference
        exclude = ["created_at", "updated_at"]


class ClaimResponseAddItemRequestReferenceReferenceSerializer(
    BaseReferenceModelSerializer
):
    """ClaimResponse Request Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseAddItemRequestReference
        exclude = ["created_at", "updated_at"]


class ClaimResponseItemAdjudicationSerializer(WritableNestedModelSerializer):
    """ClaimResponse Item Adjudication serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    reason = CodeableConceptSerializer(many=False, required=False)
    amount = MoneySerializer(many=False, required=False)
    quantity = QuantitySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseItemAdjudication
        exclude = ["created_at", "updated_at"]


class ClaimResponseItemReviewOutcomeSerializer(WritableNestedModelSerializer):
    """ClaimResponse Item Review Outcome serializer."""

    decision = CodeableConceptSerializer(many=False, required=False)
    reason = CodeableConceptSerializer(many=True, required=False)
    pre_auth_period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseItemReviewOutcome
        exclude = ["created_at", "updated_at"]


class ClaimResponseAddItemDetailSubDetailSerializer(WritableNestedModelSerializer):
    """ClaimResponse Add Item Detail Sub Detail serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    revenue = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    product_or_service_end = CodeableConceptSerializer(many=False, required=False)
    modifier = CodeableConceptSerializer(many=True, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    tax = MoneySerializer(many=False, required=False)
    net = MoneySerializer(many=False, required=False)
    review_outcome = ClaimResponseItemReviewOutcomeSerializer(
        many=False, required=False
    )
    adjudication = ClaimResponseItemAdjudicationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseAddItemDetailSubDetail
        exclude = ["created_at", "updated_at"]


class ClaimResponseAddItemDetailSerializer(WritableNestedModelSerializer):
    """ClaimResponse Add Item Detail serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    revenue = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    product_or_service_end = CodeableConceptSerializer(many=False, required=False)
    modifier = CodeableConceptSerializer(many=True, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    tax = MoneySerializer(many=False, required=False)
    net = MoneySerializer(many=False, required=False)
    review_outcome = ClaimResponseItemReviewOutcomeSerializer(
        many=False, required=False
    )
    adjudication = ClaimResponseItemAdjudicationSerializer(many=True, required=False)
    sub_detail = ClaimResponseAddItemDetailSubDetailSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = ClaimResponseAddItemDetail
        exclude = ["created_at", "updated_at"]


class ClaimResponseAddItemBodySiteSerializer(WritableNestedModelSerializer):
    """ClaimResponse Body Site Reference serializer."""

    site = BodyStructureCodeableReferenceSerializer(many=True, required=False)
    sub_site = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseAddItemBodySite
        exclude = ["created_at", "updated_at"]


class ClaimResponseAddItemSerializer(WritableNestedModelSerializer):
    """ClaimResponse Add Item serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    provider = ClaimResponseAddItemProviderReferenceReferenceSerializer(
        many=False, required=False
    )
    revenue = CodeableConceptSerializer(many=False, required=False)
    product_or_service = CodeableConceptSerializer(many=False, required=False)
    product_or_service_end = CodeableConceptSerializer(many=False, required=False)
    request = ClaimResponseAddItemRequestReferenceReferenceSerializer(
        many=True, required=False
    )
    modifier = CodeableConceptSerializer(many=True, required=False)
    program_code = CodeableConceptSerializer(many=True, required=False)
    serviced_period = PeriodSerializer(many=False, required=False)
    location_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    location_address = AddressSerializer(many=False, required=False)
    location_reference = LocationReferenceSerializer(many=False, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    tax = MoneySerializer(many=False, required=False)
    net = MoneySerializer(many=False, required=False)
    body_site = ClaimResponseAddItemBodySiteSerializer(many=False, required=False)
    review_outcome = ClaimResponseItemReviewOutcomeSerializer(
        many=False, required=False
    )
    adjudication = ClaimResponseItemAdjudicationSerializer(many=True, required=False)
    detail = ClaimResponseAddItemDetailSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseAddItem
        exclude = ["created_at", "updated_at"]


class ClaimResponseItemDetailSubDetailSerializer(WritableNestedModelSerializer):
    """ClaimResponse Item Detail Sub Detail serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    review_outcome = ClaimResponseItemReviewOutcomeSerializer(
        many=False, required=False
    )
    adjudication = ClaimResponseItemAdjudicationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseItemDetailSubDetail
        exclude = ["created_at", "updated_at"]


class ClaimResponseItemDetailSerializer(WritableNestedModelSerializer):
    """ClaimResponse Item Detail serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    review_outcome = ClaimResponseItemReviewOutcomeSerializer(
        many=False, required=False
    )
    adjudication = ClaimResponseItemAdjudicationSerializer(many=True, required=False)
    sub_detail = ClaimResponseItemDetailSubDetailSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseItemDetail
        exclude = ["created_at", "updated_at"]


class ClaimResponseItemSerializer(WritableNestedModelSerializer):
    """ClaimResponse Item serializer."""

    trace_number = IdentifierSerializer(many=True, required=False)
    review_outcome = ClaimResponseItemReviewOutcomeSerializer(
        many=False, required=False
    )
    adjudication = ClaimResponseItemAdjudicationSerializer(many=True, required=False)
    detail = ClaimResponseItemDetailSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseItem
        exclude = ["created_at", "updated_at"]


class ClaimResponseRequestorReferenceSerializer(BaseReferenceModelSerializer):
    """ClaimResponse Requestor reference serializer."""  # codespell:ignore requestor

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseRequestorReference
        exclude = ["created_at", "updated_at"]


class ClaimResponseErrorSerializer(WritableNestedModelSerializer):
    """ClaimResponse Error serializer."""

    code = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseError
        exclude = ["created_at", "updated_at"]


class ClaimResponseEventSerializer(WritableNestedModelSerializer):
    """ClaimResponse Event serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    when_period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseEvent
        exclude = ["created_at", "updated_at"]


class ClaimResponsePaymentSerializer(WritableNestedModelSerializer):
    """ClaimResponse Payment serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    adjustment = MoneySerializer(many=False, required=False)
    adjustment_reason = CodeableConceptSerializer(many=False, required=False)
    amount = MoneySerializer(many=False, required=False)
    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponsePayment
        exclude = ["created_at", "updated_at"]


class ClaimResponseTotalSerializer(WritableNestedModelSerializer):
    """ClaimResponse Total serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    amount = MoneySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseTotal
        exclude = ["created_at", "updated_at"]


class ClaimResponseInsuranceSerializer(WritableNestedModelSerializer):
    """ClaimResponse Insurance serializer."""

    coverage = CoverageReferenceSerializer(many=False, required=False)
    claimResponse = ClaimResponseReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseInsurance
        exclude = ["created_at", "updated_at"]


class ClaimResponseProcessNoteSerializer(WritableNestedModelSerializer):
    """ClaimResponse Process Note serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    language = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponseProcessNote
        exclude = ["created_at", "updated_at"]


class ClaimResponseSerializer(BaseWritableNestedModelSerializer):
    """ClaimResponse serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    trace_number = IdentifierSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    sub_type = CodeableConceptSerializer(many=False, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)
    insurer = OrganizationReferenceSerializer(many=False, required=False)
    requestor = ClaimResponseRequestorReferenceSerializer(  # codespell:ignore requestor
        many=False, required=False
    )
    request = ClaimReferenceSerializer(many=False, required=False)
    decision = CodeableConceptSerializer(many=False, required=False)
    pre_auth_period = PeriodSerializer(many=False, required=False)
    event = ClaimResponseEventSerializer(many=True, required=False)
    payee_type = CodeableConceptSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    diagnosis_related_group = CodeableConceptSerializer(many=False, required=False)
    item = ClaimResponseItemSerializer(many=True, required=False)
    add_item = ClaimResponseAddItemSerializer(many=True, required=False)
    adjudication = ClaimResponseItemAdjudicationSerializer(many=True, required=False)
    total = ClaimResponseTotalSerializer(many=True, required=False)
    payment = ClaimResponsePaymentSerializer(many=False, required=False)
    funds_reserve = CodeableConceptSerializer(many=False, required=False)
    form_code = CodeableConceptSerializer(many=False, required=False)
    form = AttachmentSerializer(many=False, required=False)
    process_note = ClaimResponseProcessNoteSerializer(many=True, required=False)
    # communication_request = CommunicationRequestReferenceSerializer(many=True, required=False)
    insurance = ClaimResponseInsuranceSerializer(many=True, required=False)
    error = ClaimResponseErrorSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClaimResponse
        exclude = ["created_at", "updated_at"]
