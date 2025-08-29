"""charge item serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.accounts.serializers import AccountReferenceSerializer
from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    MonetaryComponentSerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    QuantitySerializer,
    ReferenceSerializer,
    TimingSerializer,
)
from dfhir.bodystructures.serializers import BodyStructureReferenceSerializer
from dfhir.chargeitems.models import (
    ChargeItem,
    ChargeItemEntererReference,
    ChargeItemPerformer,
    ChargeItemPerformerActorReference,
    ChargeItemProductCodeableReference,
    ChargeItemProductReference,
    ChargeItemReasonCodeableReference,
    ChargeItemReasonReference,
    ChargeItemReference,
    ChargeItemServiceCodealbeReference,
    ChargeItemServiceReference,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.patients.serializers import PatientGroupReferenceSerializer


class ChargeItemReferenceSerializer(BaseReferenceModelSerializer):
    """Charge item reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ChargeItemReference
        exclude = ["created_at", "updated_at"]


class ChargeItemPerformerActorReferenceSerializer(BaseReferenceModelSerializer):
    """Charge item performer actor reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta  options."""

        model = ChargeItemPerformerActorReference
        exclude = ["created_at", "updated_at"]


class ChargeItemPerformerSerializer(WritableNestedModelSerializer):
    """charge item performer serializer."""

    function = CodeableConceptSerializer(many=False, required=False)
    actor = ChargeItemPerformerActorReferenceSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ChargeItemPerformer
        exclude = ["created_at", "updated_at"]


class ChargeItemEntererReferenceSerializer(BaseReferenceModelSerializer):
    """Charge item enterer reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ChargeItemEntererReference
        exclude = ["created_at", "updated_at"]


class ChargeItemsServiceReference(BaseReferenceModelSerializer):
    """Charge item service reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ChargeItemServiceReference
        exclude = ["created_at", "updated_at"]


class ChargeItemProductReferenceSerializer(BaseReferenceModelSerializer):
    """Charge item product reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ChargeItemProductReference
        exclude = ["created_at", "updated_at"]


class ChargeItemProductCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Charge item product codeable reference serializer."""

    concept = CodeableConceptSerializer(many=False, required=False)
    reference = ChargeItemProductReferenceSerializer(required=False)

    class Meta:
        """Meta options."""

        model = ChargeItemProductCodeableReference
        exclude = ["created_at", "updated_at"]


class ChargeItemReasonReferenceSerializer(BaseReferenceModelSerializer):
    """Charge item reason reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ChargeItemReasonReference
        exclude = ["created_at", "updated_at"]


class ChargeItemReasonCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Charge item reason codeable reference serializer."""

    concept = CodeableConceptSerializer(many=False, required=False)
    reference = ChargeItemReasonReferenceSerializer(required=False)

    class Meta:
        """Meta options."""

        model = ChargeItemReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class ChargeItemServiceCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Charge item service codeable reference serializer."""

    concept = CodeableConceptSerializer(many=False, required=False)
    reference = ChargeItemsServiceReference(required=False)

    class Meta:
        """Meta options."""

        model = ChargeItemServiceCodealbeReference
        exclude = ["created_at", "updated_at"]


class ChargeItemSerializer(BaseWritableNestedModelSerializer):
    """charge item serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    part_of = ChargeItemReferenceSerializer(many=False, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    subject = PatientGroupReferenceSerializer(required=False)
    encounter = EncounterReferenceSerializer(required=False)
    occurrence_period = PeriodSerializer(required=False)
    occurrence_timing = TimingSerializer(required=False)
    performer = ChargeItemPerformerSerializer(many=True, required=False)
    performing_organization = OrganizationReferenceSerializer(required=False)
    requesting_organization = OrganizationReferenceSerializer(required=False)
    cost_center = OrganizationReferenceSerializer(required=False)
    quantity = QuantitySerializer(required=False)
    body_site = BodyStructureReferenceSerializer(many=False, required=False)
    unit_price_component = MonetaryComponentSerializer(many=False, required=False)
    total_price_component = MonetaryComponentSerializer(many=False, required=False)
    override_reason = CodeableConceptSerializer(required=False)
    enterer = ChargeItemEntererReferenceSerializer(required=False)
    reason = ChargeItemReasonCodeableReferenceSerializer(many=True, required=False)
    service = ChargeItemServiceCodeableReferenceSerializer(many=True, required=False)
    product = ChargeItemProductCodeableReferenceSerializer(many=True, required=False)
    account = AccountReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    supporting_information = ReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = ChargeItem
        exclude = ["created_at", "updated_at"]
