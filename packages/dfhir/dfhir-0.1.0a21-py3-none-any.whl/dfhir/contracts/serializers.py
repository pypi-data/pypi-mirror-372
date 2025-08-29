"""Contract serializer."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework_recursive.fields import RecursiveField

from dfhir.base.serializers import (
    AnnotationSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodingSerializer,
    IdentifierSerializer,
    MoneySerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    QuantitySerializer,
    ReferenceSerializer,
    SignatureSerializer,
    SimpleQuantitySerializer,
    TimingSerializer,
)
from dfhir.encounters.serializers import EncounterEpisodeOfCareReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.provenances.serializers import ProvenanceReferenceSerializer

from .models import (
    Contract,
    ContractAuthorReference,
    ContractContentDefinition,
    ContractContentDefinitionPublisherReference,
    ContractFriendly,
    ContractFriendlyContentReferenceReference,
    ContractLegal,
    ContractLegalContentReferenceReference,
    ContractLegallyBindingReferenceReference,
    ContractReference,
    ContractRule,
    ContractSigner,
    ContractSignerPartyReference,
    ContractSubjectReference,
    ContractTerm,
    ContractTermAction,
    ContractTermActionPerformerReference,
    ContractTermActionReasonCodeableReference,
    ContractTermActionReasonReference,
    ContractTermActionRequesterReference,
    ContractTermActionSubject,
    ContractTermActionSubjectReferenceReference,
    ContractTermAsset,
    ContractTermAssetContext,
    ContractTermAssetValuedItem,
    ContractTermAssetValuedItemRecipientReference,
    ContractTermAssetValuedItemResponsibleReference,
    ContractTermOffer,
    ContractTermOfferAnswer,
    ContractTermOfferParty,
    ContractTermOfferPartyReferenceReference,
    ContractTermSecurityLabel,
)


class ContractSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """Contract Subject Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractSubjectReference
        exclude = ["created_at", "updated_at"]

    # def to_internal_value(self, data):
    #     """To internal value."""
    #     breakpoint()
    #     x = super().to_internal_value(data)
    #     return x


class ContractReferenceSerializer(BaseReferenceModelSerializer):
    """Contract reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractReference
        exclude = ["created_at", "updated_at"]


class ContractRuleSerializer(WritableNestedModelSerializer):
    """Contract Rule serializer."""

    content_attachment = AttachmentSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractRule
        exclude = ["created_at", "updated_at"]


class ContractLegalContentReferenceReferenceSerializer(BaseReferenceModelSerializer):
    """Contract Legal Content Reference Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractLegalContentReferenceReference
        exclude = ["created_at", "updated_at"]


class ContractLegalSerializer(WritableNestedModelSerializer):
    """Contract Legal serializer."""

    content_attachment = AttachmentSerializer(many=False, required=False)
    content_reference = ContractLegalContentReferenceReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = ContractLegal
        exclude = ["created_at", "updated_at"]


class ContractSignerPartyReferenceSerializer(BaseReferenceModelSerializer):
    """Contract Signer Party Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractSignerPartyReference
        exclude = ["created_at", "updated_at"]


class ContractSignerSerializer(WritableNestedModelSerializer):
    """Contract Signer serializer."""

    type = CodingSerializer(many=False, required=False)
    party = ContractSignerPartyReferenceSerializer(many=False, required=False)
    signature = SignatureSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ContractSigner
        exclude = ["created_at", "updated_at"]


class ContractFriendlyContentReferenceReferenceSerializer(BaseReferenceModelSerializer):
    """Contract Friendly Content Reference Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractFriendlyContentReferenceReference
        exclude = ["created_at", "updated_at"]


class ContractFriendlySerializer(WritableNestedModelSerializer):
    """Contract Friendly serializer."""

    content_attachment = AttachmentSerializer(many=False, required=False)
    content_reference = ContractFriendlyContentReferenceReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = ContractFriendly
        exclude = ["created_at", "updated_at"]


class ContractTermOfferPartyReferenceReferenceSerializer(BaseReferenceModelSerializer):
    """Contract Term Offer Party Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermOfferPartyReferenceReference
        exclude = ["created_at", "updated_at"]


class ContractTermOfferPartySerializer(WritableNestedModelSerializer):
    """Contract Term Offer Party serializer."""

    reference = ContractTermOfferPartyReferenceReferenceSerializer(
        many=True, required=False
    )
    role = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermOfferParty
        exclude = ["created_at", "updated_at"]


class ContractTermOfferAnswerSerializer(WritableNestedModelSerializer):
    """Contract Term Offer Answer serializer."""

    value_attachment = AttachmentSerializer(many=False, required=False)
    value_coding = CodingSerializer(many=False, required=False)
    value_quantity = QuantitySerializer(many=False, required=False)
    value_reference = ReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermOfferAnswer
        exclude = ["created_at", "updated_at"]


class ContractTermOfferSerializer(WritableNestedModelSerializer):
    """Contract Term Offer serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    party = ContractTermOfferPartySerializer(many=True, required=False)
    topic = ReferenceSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    decision = CodeableConceptSerializer(many=False, required=False)
    decision_mode = CodeableConceptSerializer(many=True, required=False)
    answer = ContractTermOfferAnswerSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermOffer
        exclude = ["created_at", "updated_at"]


class ContractTermAssetContextSerializer(WritableNestedModelSerializer):
    """Contract Term Asset Context serializer."""

    reference = ReferenceSerializer(many=False, required=False)
    code = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermAssetContext
        exclude = ["created_at", "updated_at"]


class ContractTermAssetValuedItemResponsibleReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Contract Term Asset Valued Item Responsible Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermAssetValuedItemResponsibleReference
        exclude = ["created_at", "updated_at"]


class ContractTermAssetValuedItemRecipientReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Contract Term Asset Valued Item Recipient Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermAssetValuedItemRecipientReference
        exclude = ["created_at", "updated_at"]


class ContractTermAssetValuedItemSerializer(WritableNestedModelSerializer):
    """Contract Term Asset Valued Item serializer."""

    entity_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    entity_reference = ReferenceSerializer(many=False, required=False)
    identifier = IdentifierSerializer(many=False, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    unit_price = MoneySerializer(many=False, required=False)
    net = MoneySerializer(many=False, required=False)
    responsible = ContractTermAssetValuedItemResponsibleReferenceSerializer(
        many=False, required=False
    )
    recipient = ContractTermAssetValuedItemRecipientReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = ContractTermAssetValuedItem
        exclude = ["created_at", "updated_at"]


class ContractTermAssetSerializer(WritableNestedModelSerializer):
    """Contract Term Asset serializer."""

    scope = CodeableConceptSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    type_reference = ReferenceSerializer(many=True, required=False)
    subtype = CodeableConceptSerializer(many=True, required=False)
    relationship = CodingSerializer(many=False, required=False)
    context = ContractTermAssetContextSerializer(many=True, required=False)
    period_type = CodeableConceptSerializer(many=True, required=False)
    period = PeriodSerializer(many=True, required=False)
    use_period = PeriodSerializer(many=True, required=False)
    answer = ContractTermOfferAnswerSerializer(many=True, required=False)
    valued_item = ContractTermAssetValuedItemSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermAsset
        exclude = ["created_at", "updated_at"]


class ContractTermActionSubjectReferenceReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Contract Term Action Subject Reference Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermActionSubjectReferenceReference
        exclude = ["created_at", "updated_at"]


class ContractTermActionSubjectSerializer(WritableNestedModelSerializer):
    """Contract Term Action Subject serializer."""

    reference = ContractTermActionSubjectReferenceReferenceSerializer(
        many=True, required=False
    )
    role = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermActionSubject
        exclude = ["created_at", "updated_at"]


class ContractTermActionRequesterReferenceSerializer(WritableNestedModelSerializer):
    """Contract Term Action Requester Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermActionRequesterReference
        exclude = ["created_at", "updated_at"]


class ContractTermActionPerformerReferenceSerializer(BaseReferenceModelSerializer):
    """Contract Term Action Performer Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermActionPerformerReference
        exclude = ["created_at", "updated_at"]


class ContractTermActionReasonReferenceSerializer(WritableNestedModelSerializer):
    """Contract Term Action Reason Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermActionReasonReference
        exclude = ["created_at", "updated_at"]


class ContractTermActionReasonCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """Contract Term Action Reason Codeable Reference serializer."""

    reference = ContractTermActionReasonReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermActionReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class ContractTermActionSerializer(WritableNestedModelSerializer):
    """Contract Term Action serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    subject = ContractTermActionSubjectSerializer(many=True, required=False)
    intent = CodeableConceptSerializer(many=False, required=False)
    status = CodeableConceptSerializer(many=False, required=False)
    context = EncounterEpisodeOfCareReferenceSerializer(many=False, required=False)
    occurrence_period = PeriodSerializer(many=False, required=False)
    occurrence_timing = TimingSerializer(many=False, required=False)
    requester = ContractTermActionRequesterReferenceSerializer(
        many=False, required=False
    )
    performer_type = CodeableConceptSerializer(many=True, required=False)
    performer_role = CodeableConceptSerializer(many=False, required=False)
    performer = ContractTermActionPerformerReferenceSerializer(
        many=False, required=False
    )
    reason = ContractTermActionReasonCodeableReferenceSerializer(
        many=True, required=False
    )
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermAction
        exclude = ["created_at", "updated_at"]


class ContractAuthorReferenceSerializer(BaseReferenceModelSerializer):
    """Contract Author Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractAuthorReference
        exclude = ["created_at", "updated_at"]


class ContractContentDefinitionPublisherReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Contract Content Definition Publisher Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractContentDefinitionPublisherReference
        exclude = ["created_at", "updated_at"]


class ContractContentDefinitionSerializer(WritableNestedModelSerializer):
    """Contract Content Definition serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    sub_type = CodeableConceptSerializer(many=False, required=False)
    publisher = ContractContentDefinitionPublisherReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = ContractContentDefinition
        exclude = ["created_at", "updated_at"]


class ContractTermSecurityLabelSerializer(WritableNestedModelSerializer):
    """Contract Term Security Label serializer."""

    classification = CodingSerializer(many=False, required=False)
    category = CodingSerializer(many=True, required=False)
    control = CodingSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ContractTermSecurityLabel
        exclude = ["created_at", "updated_at"]


class ContractLegallyBindingReferenceReferenceSerializer(BaseReferenceModelSerializer):
    """Contract Legally Binding Reference Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContractLegallyBindingReferenceReference
        exclude = ["created_at", "updated_at"]


class ContractTermSerializer(WritableNestedModelSerializer):
    """Contract Term serializer."""

    identifier = IdentifierSerializer(many=False, required=False)
    applies = PeriodSerializer(many=False, required=False)
    topic_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    topic_reference = ReferenceSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    sub_type = CodeableConceptSerializer(many=False, required=False)
    security_label = ContractTermSecurityLabelSerializer(many=False, required=False)
    offer = ContractTermOfferSerializer(many=False, required=False)
    asset = ContractTermAssetSerializer(many=True, required=False)
    action = ContractTermActionSerializer(many=True, required=False)
    group = RecursiveField(
        "ContractTermSerializer", many=True, required=False
    )  # TODO need to fix this as it currently throws an error.

    class Meta:
        """Meta class."""

        model = ContractTerm
        exclude = ["created_at", "updated_at"]


class ContractSerializer(BaseWritableNestedModelSerializer):
    """Contract serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    legal_state = CodeableConceptSerializer(many=False, required=False)
    instantiates_canonical = ContractReferenceSerializer(many=False, required=False)
    content_derivative = CodeableConceptSerializer(many=False, required=False)
    applies = PeriodSerializer(many=False, required=False)
    expiration_type = CodeableConceptSerializer(many=False, required=False)
    subject = ContractSubjectReferenceSerializer(many=True, required=False)
    authority = OrganizationReferenceSerializer(many=True, required=False)
    domain = LocationReferenceSerializer(many=True, required=False)
    author = ContractAuthorReferenceSerializer(many=False, required=False)
    scope = CodeableConceptSerializer(many=False, required=False)
    topic_codeable_concept = CodeableConceptSerializer(many=True, required=False)
    topic_reference = ReferenceSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    sub_type = CodeableConceptSerializer(many=True, required=False)
    content_definition = ContractContentDefinitionSerializer(many=False, required=False)
    term = ContractTermSerializer(many=True, required=False)
    supporting_info = ReferenceSerializer(many=True, required=False)
    relevant_history = ProvenanceReferenceSerializer(many=True, required=False)
    signer = ContractSignerSerializer(many=True, required=False)
    friendly = ContractFriendlySerializer(many=True, required=False)
    legal = ContractLegalSerializer(many=True, required=False)
    rule = ContractRuleSerializer(many=True, required=False)
    legally_binding_attachment = AttachmentSerializer(many=False, required=False)
    legally_binding_reference = ContractLegallyBindingReferenceReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = Contract
        exclude = ["created_at", "updated_at"]
