"""groups serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodingSerializer,
    ContactDetailSerializer,
    ExpressionSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    QuantitySerializer,
    RangeSerializer,
    ReferenceSerializer,
    RelativeTimeSerializer,
    UsageContextSerializer,
)

from .models import (
    Group,
    GroupCharacteristic,
    GroupCharacteristicDeterminedByReference,
    GroupManagingEntityReference,
    GroupMember,
    GroupMemberEntityReference,
    GroupReference,
)


class GroupCharacteristicDeterminedByReferenceSerializer(BaseReferenceModelSerializer):
    """Group Characteristic Determined By Reference Serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = GroupCharacteristicDeterminedByReference
        exclude = ["created_at", "updated_at"]


class GroupCharacteristicSerializer(WritableNestedModelSerializer):
    """Group Characteristic Serializer."""

    code = CodeableConceptSerializer(many=False, required=False)
    value_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    value_quantity = QuantitySerializer(many=False, required=False)
    value_range = RangeSerializer(many=False, required=False)
    value_reference = ReferenceSerializer(many=False, required=False)
    value_expression = ExpressionSerializer(many=False, required=False)
    valueRange = RangeSerializer(many=False, required=False)
    valueExpression = ExpressionSerializer(many=False, required=False)
    method = CodeableConceptSerializer(many=True, required=False)
    determined_by_reference = GroupCharacteristicDeterminedByReferenceSerializer(
        many=False, required=False
    )
    determined_by_expression = ExpressionSerializer(many=False, required=False)
    offset = CodeableConceptSerializer(many=False, required=False)
    instances_quantity = QuantitySerializer(many=False, required=False)
    instances_range = RangeSerializer(many=False, required=False)
    duration_duration = QuantitySerializer(many=False, required=False)
    duration_range = RangeSerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)
    timing = RelativeTimeSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = GroupCharacteristic
        exclude = ["created_at", "updated_at"]


class GroupManagingEntityReferenceSerializer(BaseReferenceModelSerializer):
    """Group Managing Entity Reference Serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = GroupManagingEntityReference
        exclude = ["created_at", "updated_at"]


class GroupMemberEntityReferenceSerializer(BaseReferenceModelSerializer):
    """Group Member Entity Reference Serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = GroupMemberEntityReference
        exclude = ["created_at", "updated_at"]


class GroupMemberSerializer(WritableNestedModelSerializer):
    """Group Member Serializer."""

    entity = GroupMemberEntityReferenceSerializer(many=False, required=False)
    involvement = CodeableConceptSerializer(many=True, required=False)
    period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = GroupMember
        exclude = ["created_at", "updated_at"]


class GroupSerializer(BaseWritableNestedModelSerializer):
    """Group Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    version_algorithm_coding = CodingSerializer(many=False, required=False)
    contact = ContactDetailSerializer(many=True, required=False)
    use_context = UsageContextSerializer(many=True, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    characteristic = GroupCharacteristicSerializer(many=True, required=False)
    managing_entity = GroupManagingEntityReferenceSerializer(many=False, required=False)
    member = GroupMemberSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = Group
        exclude = ["created_at", "updated_at"]


class GroupReferenceSerializer(BaseReferenceModelSerializer):
    """Group Reference Serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = GroupReference
        exclude = ["created_at", "updated_at"]
