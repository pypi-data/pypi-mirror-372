"""Flag serializers."""

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer

from .models import (
    Flag,
    FlagAuthorReference,
    FlagSubjectReference,
    FlagSupportingInfoReference,
)


class FlagSupportingInfoReferenceSerializer(BaseReferenceModelSerializer):
    """FlagSupportingInfoReference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = FlagSupportingInfoReference
        exclude = ["created_at", "updated_at"]


class FlagAuthorReferenceSerializer(BaseReferenceModelSerializer):
    """FlagAuthorReference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = FlagAuthorReference
        exclude = ["created_at", "updated_at"]


class FlagSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """FlagSubjectReference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = FlagSubjectReference
        exclude = ["created_at", "updated_at"]


class FlagSerializer(BaseWritableNestedModelSerializer):
    """Flag serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    subject = FlagSubjectReferenceSerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    author = FlagAuthorReferenceSerializer(many=False, required=False)
    supporting_info = FlagSupportingInfoReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Flag
        exclude = ["created_at", "updated_at"]
