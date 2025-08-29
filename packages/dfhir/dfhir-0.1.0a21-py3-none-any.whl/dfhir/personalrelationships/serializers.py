"""Personal Relationships serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
)
from dfhir.groups.serializers import GroupReferenceSerializer

from .models import (
    PersonalRelationship,
    PersonalRelationshipAsserterReference,
    PersonalRelationshipSourceReference,
    PersonalRelationshipTargetReference,
)


class PersonalRelationshipSourceReferenceSerializer(BaseReferenceModelSerializer):
    """Personal Relationship Source Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PersonalRelationshipSourceReference
        exclude = ["created_at", "updated_at"]


class PersonalRelationshipTargetReferenceSerializer(BaseReferenceModelSerializer):
    """Personal Relationship Source Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PersonalRelationshipTargetReference
        exclude = ["created_at", "updated_at"]


class PersonalRelationshipAsserterReferenceSerializer(BaseReferenceModelSerializer):
    """Personal Relationship Asserter Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = PersonalRelationshipAsserterReference
        exclude = ["created_at", "updated_at"]


class PersonalRelationshipSerializer(WritableNestedModelSerializer):
    """Personal Relationship serializer."""

    source = PersonalRelationshipSourceReferenceSerializer(required=False)
    target = PersonalRelationshipTargetReferenceSerializer(required=False)
    asserter = PersonalRelationshipAsserterReferenceSerializer(required=False)
    relationship_type = CodeableConceptSerializer(required=False)
    confidence = CodeableConceptSerializer(required=False)
    period = PeriodSerializer(many=True, required=False)
    group = GroupReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = PersonalRelationship
        exclude = ["created_at", "updated_at"]
