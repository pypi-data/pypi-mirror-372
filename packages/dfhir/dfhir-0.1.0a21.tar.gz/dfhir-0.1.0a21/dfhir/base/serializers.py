"""Base serializers."""

import inspect
from typing import Any, TypeVar

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from . import utils
from .models import (
    Address,
    Age,
    Annotation,
    Attachment,
    Availability,
    AvailableTime,
    CodeableConcept,
    CodeableReference,
    Coding,
    Communication,
    ContactDetail,
    ContactPoint,
    Duration,
    Expression,
    ExtendedContactDetail,
    HumanName,
    Identifier,
    MonetaryComponent,
    Money,
    NotAvailableTime,
    OrganizationReference,
    Payload,
    Period,
    ProductShelfLife,
    Qualification,
    Quantity,
    Range,
    Ratio,
    Reference,
    RelatedArtifact,
    RelativeTime,
    Repeat,
    Signature,
    SignatureOnBehalfOfReference,
    SignatureWhoReference,
    SimpleQuantity,
    Timing,
    TriggerDefinition,
    UsageContext,
    VirtualServiceDetailAddress,
    VirtualServiceDetails,
)

_VT = TypeVar("_VT")
_DT = TypeVar("_DT")
_IN = TypeVar("_IN")


class RenameFieldsMixin(serializers.ModelSerializer):
    """Rename fields mixin."""

    def __init__(self, *args, **kwargs):
        """Initialize the serializer and set up field renaming."""
        super().__init__(*args, **kwargs)
        self.rename_fields = getattr(self.Meta, "rename_fields", {})

    def to_representation(self, instance: _IN) -> dict[str, Any]:
        """Rename fields in the output data."""
        data = super().to_representation(instance)
        for new_field, original_field in self.rename_fields.items():
            if original_field in data:
                data[new_field] = data.pop(original_field)
        return data

    def to_internal_value(self, data: _DT) -> _VT:
        """Rename fields in the input data."""
        for new_field, original_field in self.rename_fields.items():
            if new_field in data:
                data[original_field] = data.pop(new_field)

        return super().to_internal_value(data)

    def get_fields(self) -> dict[str, serializers.Field]:
        """Rename fields in the serializer definition."""
        for new_field, original_field in self.rename_fields.items():
            if new_field in self._declared_fields:
                self._declared_fields[original_field] = self._declared_fields.pop(
                    new_field
                )
        return super().get_fields()


class BaseModelSerializer(RenameFieldsMixin, serializers.ModelSerializer):
    """Base model serializer."""

    def get_fields(self) -> dict[str, serializers.Field]:
        """Get fields."""
        fields = super().get_fields()
        fields["resource_type"] = serializers.ReadOnlyField()
        return fields


class BaseWritableNestedModelSerializer(
    RenameFieldsMixin, WritableNestedModelSerializer
):
    """Base writable nested model serializer."""

    def get_fields(self) -> dict[str, serializers.Field]:
        """Get fields."""
        fields = super().get_fields()
        fields["resource_type"] = serializers.ReadOnlyField()
        return fields


class BaseReferenceModelSerializer(WritableNestedModelSerializer):
    """Base reference model serializer."""

    def to_internal_value(self, data: _DT) -> _VT:
        """Convert reference to internal value."""
        try:
            ref = data.get("reference")
            if ref and isinstance(ref, str):
                key, value = ref.split("/")
                data[utils.to_snake_case(key)] = int(value)
        except AttributeError as e:
            raise AttributeError(
                f"{e} |  ModelClass: {self.Meta.model.__name__}  -  serializerClass: {self.__class__.__name__} -  data: {data}"
            ) from e
        except Exception as e:
            raise serializers.ValidationError(
                f"Invalid reference: {ref}. References should be in the format '<ResourceName>/[id]'"
            ) from e
        return super().to_internal_value(data)


class OrganizationReferenceSerializer(BaseReferenceModelSerializer):
    """Organization reference serializer."""

    def get_fields(self):
        """Get fields."""
        fields = super().get_fields()
        frames = inspect.stack()

        for frame in frames:
            if "drf_spectacular" in frame.filename:
                # when generating docs using drf_spectacular, skip the identifier field
                # to avoid a recursive loop.
                return fields

        fields["identifier"] = IdentifierSerializer(required=False, many=False)
        return fields

    class Meta:
        """Meta class."""

        model = OrganizationReference
        exclude = [
            "created_at",
            "updated_at",
        ]


class CodingSerializer(serializers.ModelSerializer):
    """Coding serializer."""

    class Meta:
        """Meta class."""

        model = Coding
        exclude = ["created_at", "updated_at"]


class CodeableConceptSerializer(WritableNestedModelSerializer):
    """CodeableConcept serializer."""

    coding = CodingSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = CodeableConcept
        exclude = ["created_at", "updated_at"]


class PeriodSerializer(serializers.ModelSerializer):
    """Period serializer."""

    class Meta:
        """Meta class."""

        model = Period
        exclude = ["created_at", "updated_at"]


class IdentifierSerializer(WritableNestedModelSerializer):
    """Identifier serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)
    assigner = OrganizationReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Identifier
        exclude = ["created_at", "updated_at"]


class QualificationSerializer(WritableNestedModelSerializer):
    """Qualification serializer."""

    code = CodeableConceptSerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)
    identifier = IdentifierSerializer(many=True, required=False)
    issuer = OrganizationReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Qualification
        exclude = ["created_at", "updated_at"]


class AddressSerializer(WritableNestedModelSerializer):
    """Address serializer."""

    period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Address
        exclude = ["created_at", "updated_at"]


class HumanNameSerializer(WritableNestedModelSerializer):
    """HumanName serializer."""

    period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = HumanName
        exclude = ["created_at", "updated_at"]


class ContactPointSerializer(WritableNestedModelSerializer):
    """ContactPoint serializer."""

    period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ContactPoint
        exclude = ["created_at", "updated_at"]


class ExtendedContactDetailSerializer(WritableNestedModelSerializer):
    """ExtendedContactDetail serializer."""

    name = HumanNameSerializer(many=True, required=False)
    address = AddressSerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)
    telecom = ContactPointSerializer(many=True, required=False)
    purpose = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ExtendedContactDetail
        exclude = ["created_at", "updated_at"]


class PayloadSerializer(WritableNestedModelSerializer):
    """Payload serializer."""

    type = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Payload
        exclude = ["created_at", "updated_at"]


class AvailableTimeSerializer(serializers.ModelSerializer):
    """AvailableTime serializer."""

    class Meta:
        """Meta class."""

        model = AvailableTime
        exclude = ["created_at", "updated_at"]


class NotAvailableTimeSerializer(WritableNestedModelSerializer):
    """NotAvailableTime serializer."""

    during = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = NotAvailableTime
        exclude = ["created_at", "updated_at"]


class AvailabilitySerializer(WritableNestedModelSerializer):
    """Availability serializer."""

    period = PeriodSerializer(many=True, required=False)
    available_time = AvailableTimeSerializer(many=True, required=False)
    not_available_time = NotAvailableTimeSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Availability
        exclude = ["created_at", "updated_at"]


class VirtualServiceDetailAddressSerializer(WritableNestedModelSerializer):
    """VirtualServiceDetailAddress serializer."""

    address_contact_point = ContactPointSerializer(many=True, required=False)
    address_extended_contact_detail = ExtendedContactDetailSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = VirtualServiceDetailAddress
        exclude = ["created_at", "updated_at"]


class VirtualServiceDetailsSerializer(WritableNestedModelSerializer):
    """VirtualServiceDetails serializer."""

    channel_type = CodingSerializer(many=False, required=False)
    address = VirtualServiceDetailAddressSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = VirtualServiceDetails
        exclude = ["created_at", "updated_at"]


class AttachmentSerializer(WritableNestedModelSerializer):
    """Attachment serializer."""

    class Meta:
        """Meta class."""

        model = Attachment
        exclude = ["created_at", "updated_at"]


class QuantitySerializer(serializers.ModelSerializer):
    """Quantity serializer."""

    class Meta:
        """Meta class."""

        model = Quantity
        exclude = ["created_at", "updated_at"]


class RangeSerializer(WritableNestedModelSerializer):
    """Range serializer."""

    low = QuantitySerializer(many=False, required=False)
    high = QuantitySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Range
        exclude = ["created_at", "updated_at"]


class ReferenceSerializer(serializers.ModelSerializer):
    """Reference serializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Reference
        exclude = ["created_at", "updated_at"]


class AnnotationSerializer(WritableNestedModelSerializer):
    """Annotation serializer."""

    author_reference = ReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Annotation
        exclude = ["created_at", "updated_at"]


class CommunicationSerializer(WritableNestedModelSerializer):
    """Communication serializer."""

    language = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = Communication
        exclude = ["created_at", "updated_at"]


class RatioSerializer(WritableNestedModelSerializer):
    """Ratio serializer."""

    numerator = QuantitySerializer(many=False, required=False)
    denominator = QuantitySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Ratio
        exclude = ["created_at", "updated_at"]


class CodeableReferenceSerializer(WritableNestedModelSerializer):
    """recommendation codeable reference serializer."""

    reference = ReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = CodeableReference
        exclude = ["created_at", "updated_at"]


class RepeatSerializer(WritableNestedModelSerializer):
    """Repeat serializer."""

    bounds_duration = QuantitySerializer(many=False, required=False)
    bounds_range = RangeSerializer(many=False, required=False)
    bounds_period = PeriodSerializer(many=False, required=False)
    day_of_week = CodingSerializer(many=True, required=False)
    when = CodingSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Repeat
        exclude = ["created_at", "updated_at"]


class TimingSerializer(WritableNestedModelSerializer):
    """timing serializer."""

    repeat = RepeatSerializer(many=False, required=False)
    code = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Timing
        exclude = ["created_at", "updated_at"]


class RelatedArtifactSerializer(WritableNestedModelSerializer):
    """RelatedArtifact serializer."""

    classifier = CodeableConceptSerializer(many=False, required=False)
    document = AttachmentSerializer(many=False, required=False)
    resource_reference = ReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = RelatedArtifact
        exclude = ["created_at", "updated_at"]


class ProductShelfLifeSerializer(WritableNestedModelSerializer):
    """ProductShelfLife serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    period_duration = QuantitySerializer(many=False, required=False)
    special_precautions_for_storage = CodeableConceptSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = ProductShelfLife
        exclude = ["created_at", "updated_at"]


class UsageContextSerializer(WritableNestedModelSerializer):
    """UsageContext serializer."""

    code = CodingSerializer(many=False, required=False)
    value_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    value_quantity = QuantitySerializer(many=False, required=False)
    value_range = RangeSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = UsageContext
        exclude = ["created_at", "updated_at"]


class ContactDetailSerializer(WritableNestedModelSerializer):
    """ContactDetail serializer."""

    telecom = ContactPointSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ContactDetail
        exclude = ["created_at", "updated_at"]


class ExpressionSerializer(WritableNestedModelSerializer):
    """Expression serializer."""

    class Meta:
        """Meta class."""

        model = Expression
        exclude = ["created_at", "updated_at"]


class RelativeTimeSerializer(WritableNestedModelSerializer):
    """RelativeTime serializer."""

    context_reference = ReferenceSerializer(many=False, required=False)
    context_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    offset_duration = QuantitySerializer(many=False, required=False)
    offset_range = RangeSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = RelativeTime
        exclude = ["created_at", "updated_at"]


class AgeSerializer(QuantitySerializer):
    """Age serializer."""

    class Meta:
        """Meta class."""

        model = Age
        exclude = ["created_at", "updated_at"]


class SimpleQuantitySerializer(QuantitySerializer):
    """SimpleQuantity serializer."""

    class Meta:
        """Meta class."""

        model = SimpleQuantity
        exclude = ["created_at", "updated_at"]


class DurationSerializer(QuantitySerializer):
    """Duration serializer."""

    class Meta:
        """Meta class."""

        model = Duration
        exclude = ["created_at", "updated_at"]


class MoneySerializer(serializers.ModelSerializer):
    """Money serializer."""

    class Meta:
        """Meta class."""

        model = Money
        exclude = ["created_at", "updated_at"]


class MonetaryComponentSerializer(WritableNestedModelSerializer):
    """MonetaryComponent serializer."""

    code = CodeableConceptSerializer(many=False, required=False)
    amount = MoneySerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = MonetaryComponent
        exclude = ["created_at", "updated_at"]


class SignatureWhoReferenceSerializer(BaseReferenceModelSerializer):
    """Signature who reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = SignatureWhoReference
        exclude = ["created_at", "updated_at"]


class SignatureOnBehalfOfReferenceSerializer(BaseReferenceModelSerializer):
    """Signature on behalf of reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = SignatureOnBehalfOfReference
        exclude = ["created_at", "updated_at"]


class SignatureSerializer(WritableNestedModelSerializer):
    """Signature serializer."""

    type = CodingSerializer(many=True, required=False)
    who = SignatureWhoReferenceSerializer(many=False, required=False)
    on_behalf_of = SignatureOnBehalfOfReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Signature
        exclude = ["created_at", "updated_at"]


class TriggerDefinitionSerializer(WritableNestedModelSerializer):
    """TriggerDefinition serializer."""

    code = CodeableConceptSerializer(many=False, required=False)
    timing_timing = TimingSerializer(many=False, required=False)
    condition = ExpressionSerializer(many=False, required=False)

    def get_fields(self) -> dict[str, serializers.Field]:
        """Get fields."""
        from dfhir.schedules.serializers import ScheduleReferenceSerializer

        fields = super().get_fields()

        fields["timing_reference"] = ScheduleReferenceSerializer(
            required=False, many=False
        )
        return fields

    class Meta:
        """Meta class."""

        model = TriggerDefinition
        exclude = ["created_at", "updated_at"]
