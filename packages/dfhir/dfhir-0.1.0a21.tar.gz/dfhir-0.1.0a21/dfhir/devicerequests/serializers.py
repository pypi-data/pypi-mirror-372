"""Devicerequests serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    QuantitySerializer,
    RangeSerializer,
    ReferenceSerializer,
    TimingSerializer,
)

# from dfhir.devices.serializers import DeviceDeviceDefinitionCodeableReferenceSerializer
# from dfhir.coverages.serializers import CoverageClaimReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.provenances.serializers import ProvenanceReferenceSerializer

from .models import (
    DeviceRequest,
    DeviceRequestParameter,
    DeviceRequestPerformerCodeableReference,
    DeviceRequestPerformerReference,
    DeviceRequestReasonCodeableReference,
    DeviceRequestReasonReference,
    DeviceRequestReference,
    DeviceRequestRequesterCodeableReference,
    DeviceRequestRequesterReference,
    DeviceRequestSubjectReference,
)


class DeviceRequestReferenceSerializer(BaseReferenceModelSerializer):
    """Device Request Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = DeviceRequestReference
        exclude = ["created_at", "updated_at"]


class DeviceRequestParameterSerializer(WritableNestedModelSerializer):
    """Device Request Parameter Serializer."""

    code = CodeableConceptSerializer(many=False, required=False)
    value_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    value_quantity = QuantitySerializer(many=False, required=False)
    value_range = RangeSerializer(many=False, required=False)

    class Meta:
        """Meta."""

        model = DeviceRequestParameter
        exclude = ["created_at", "updated_at"]


class DeviceRequestPerformerReferenceSerializer(BaseReferenceModelSerializer):
    """Device Request Performer Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = DeviceRequestPerformerReference
        exclude = ["created_at", "updated_at"]


class DeviceRequestPerformerCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Device Request Performer Codeable Reference Serializer."""

    reference = DeviceRequestPerformerReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta."""

        model = DeviceRequestPerformerCodeableReference
        exclude = ["created_at", "updated_at"]


class DeviceRequestReasonReferenceSerializer(BaseReferenceModelSerializer):
    """Device Request Reason Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = DeviceRequestReasonReference
        exclude = ["created_at", "updated_at"]


class DeviceRequestReasonCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Device Request Reason Codeable Reference Serializer."""

    reference = DeviceRequestReasonReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta."""

        model = DeviceRequestReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class DeviceRequestRequesterReferenceSerializer(BaseReferenceModelSerializer):
    """Device Request Requester Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = DeviceRequestRequesterReference
        exclude = ["created_at", "updated_at"]


class DeviceRequestRequesterCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Device Request Requester Codeable Reference Serializer."""

    reference = DeviceRequestRequesterReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta."""

        model = DeviceRequestRequesterCodeableReference
        exclude = ["created_at", "updated_at"]


class DeviceRequestSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """Device Request Subject Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = DeviceRequestSubjectReference
        exclude = ["created_at", "updated_at"]


class DeviceRequestSerializer(BaseWritableNestedModelSerializer):
    """Device Request Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = ReferenceSerializer(many=True, required=False)
    replaces = DeviceRequestReferenceSerializer(many=True, required=False)
    group_identifier = IdentifierSerializer(many=False, required=False)
    # code = DeviceDeviceDefinitionCodeableReferenceSerializer(many=False, required=False)
    parameter = DeviceRequestParameterSerializer(many=True, required=False)
    subject = DeviceRequestSubjectReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    occurrence_period = PeriodSerializer(many=False, required=False)
    occurrence_timing = TimingSerializer(many=False, required=False)
    requester = DeviceRequestRequesterReferenceSerializer(many=False, required=False)
    performer = DeviceRequestPerformerCodeableReferenceSerializer(
        many=False, required=False
    )
    reason = DeviceRequestReasonCodeableReferenceSerializer(many=True, required=False)
    as_needed_for = CodeableConceptSerializer(many=False, required=False)
    # insurance = CoverageClaimReferenceSerializer(many=True, required=False)
    supporting_info = ReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    relevant_history = ProvenanceReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta."""

        model = DeviceRequest
        exclude = ["created_at", "updated_at"]
