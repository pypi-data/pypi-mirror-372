"""document reference serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodeableReferenceSerializer,
    CodingSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    ReferenceSerializer,
)
from dfhir.bodystructures.serializers import (
    BodyStructureCodeableReferenceSerializer,
    BodyStructureReferenceSerializer,
)
from dfhir.documentreferences.models import (
    DocumentReference,
    DocumentReferenceAttester,
    DocumentReferenceAttesterPartyReference,
    DocumentReferenceAuthorReference,
    DocumentReferenceBasedOnReference,
    DocumentReferenceContent,
    DocumentReferenceContentProfile,
    DocumentReferenceContextReference,
    DocumentReferenceReference,
    DocumentReferenceRelatesTo,
)


class DocumentReferenceContextReferenceSerializer(BaseReferenceModelSerializer):
    """Serializer for DocumentReferenceContextReference."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = DocumentReferenceContextReference
        exclude = ["created_at", "updated_at"]


class DocumentReferenceReferenceSerializer(BaseReferenceModelSerializer):
    """Serializer for DocumentReferenceReference."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = DocumentReferenceReference
        exclude = ["created_at", "updated_at"]


class DocumentReferenceBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """Serializer for DocumentReferenceBasedOnReference."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = DocumentReferenceBasedOnReference
        exclude = ["created_at", "updated_at"]


class DocumentReferenceAuthorReferenceSerializer(BaseReferenceModelSerializer):
    """Serializer for DocumentReferenceAuthorReference."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = DocumentReferenceAuthorReference
        exclude = ["created_at", "updated_at"]


class DocumentReferenceAttesterPartyReferenceSerializer(BaseReferenceModelSerializer):
    """Serializer for DocumentReferenceAttesterPartyReference."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = DocumentReferenceAttesterPartyReference
        exclude = ["created_at", "updated_at"]


class DocumentReferenceAttesterSerializer(WritableNestedModelSerializer):
    """Serializer for DocumentReferenceAttester."""

    mode = CodeableConceptSerializer(required=False)
    party = DocumentReferenceAttesterPartyReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = DocumentReferenceAttester
        exclude = ["created_at", "updated_at"]


class DocumentReferenceRelatesToSerializer(WritableNestedModelSerializer):
    """Serializer for DocumentReferenceRelatesTo."""

    code = CodeableConceptSerializer(required=False)
    target = DocumentReferenceReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = DocumentReferenceRelatesTo
        exclude = ["created_at", "updated_at"]


class DocumentReferenceContentProfileSerializer(WritableNestedModelSerializer):
    """Serializer for DocumentReferenceContentProfile."""

    value_coding = CodingSerializer(required=False)

    class Meta:
        """meta options."""

        model = DocumentReferenceContentProfile
        exclude = ["created_at", "updated_at"]


class DocumentReferenceContentSerializer(WritableNestedModelSerializer):
    """Serializer for DocumentReferenceContent."""

    attachment = AttachmentSerializer(required=False)
    profile = DocumentReferenceContentProfileSerializer(required=False, many=True)

    class Meta:
        """meta options."""

        model = DocumentReferenceContent
        exclude = ["created_at", "updated_at"]


class DocumentReferenceSerializer(BaseWritableNestedModelSerializer):
    """document reference writable serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    based_on = DocumentReferenceBasedOnReferenceSerializer(required=False, many=True)
    modality = CodeableConceptSerializer(required=False, many=True)
    type = CodeableConceptSerializer(required=False)
    category = CodeableConceptSerializer(required=False, many=True)
    subject = ReferenceSerializer(required=False)
    context = DocumentReferenceContextReferenceSerializer(required=False, many=True)
    event = CodeableReferenceSerializer(required=False, many=True)
    related = ReferenceSerializer(required=False, many=True)
    body_site = BodyStructureReferenceSerializer(required=False, many=True)
    body_site = BodyStructureCodeableReferenceSerializer(required=False, many=True)
    facility_type = CodeableConceptSerializer(required=False)
    practice_setting = CodeableConceptSerializer(required=False)
    period = PeriodSerializer(required=False)
    author = DocumentReferenceAuthorReferenceSerializer(required=False, many=True)
    attester = DocumentReferenceAttesterSerializer(required=False, many=True)
    custodian = OrganizationReferenceSerializer(required=False)
    relates_to = DocumentReferenceRelatesToSerializer(required=False, many=True)
    security_label = CodeableConceptSerializer(required=False, many=True)
    content = DocumentReferenceContentSerializer(required=False, many=True)

    class Meta:
        """meta options."""

        model = DocumentReference
        exclude = ["created_at", "updated_at"]
