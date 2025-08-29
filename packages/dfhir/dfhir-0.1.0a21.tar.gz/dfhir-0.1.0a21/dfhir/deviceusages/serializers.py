"""Device usage serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    TimingSerializer,
)
from dfhir.bodystructures.serializers import BodyStructureCodeableReferenceSerializer
from dfhir.devices.serializers import DeviceDeviceDefinitionCodeableReferenceSerializer
from dfhir.encounters.serializers import EncounterEpisodeOfCareReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer
from dfhir.servicerequests.serializers import ServiceRequestReferenceSerializer

from .models import (
    DeviceUsage,
    DeviceUsageAdherence,
    DeviceUsageDerivedFromReference,
    DeviceUsageInformationSourceReference,
    DeviceUsageReasonCodeableReference,
    DeviceUsageReasonReference,
)


class DeviceUsageDerivedFromReferenceSerializer(BaseReferenceModelSerializer):
    """Device usage derived from reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceUsageDerivedFromReference
        exclude = ["created_at", "updated_at"]


class DeviceUsageReasonReferenceSerializer(BaseReferenceModelSerializer):
    """Device usage reason reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceUsageReasonReference
        exclude = ["created_at", "updated_at"]


class DeviceUsageReasonCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Device usage reason codeable reference serializer."""

    reference = DeviceUsageReasonReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceUsageReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class DeviceUsageInformationSourceReferenceSerializer(BaseReferenceModelSerializer):
    """Device usage information source reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceUsageInformationSourceReference
        exclude = ["created_at", "updated_at"]


class DeviceUsageAdherenceSerializer(WritableNestedModelSerializer):
    """Device usage adherence serializer."""

    code = CodeableConceptSerializer(many=False, required=False)
    reason = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceUsageAdherence
        exclude = ["created_at", "updated_at"]


class DeviceUsageSerializer(BaseWritableNestedModelSerializer):
    """Device usage serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = ServiceRequestReferenceSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)
    derived_from = DeviceUsageDerivedFromReferenceSerializer(many=True, required=False)
    context = EncounterEpisodeOfCareReferenceSerializer(many=False, required=False)
    timing_timing = TimingSerializer(many=False, required=False)
    timing_period = PeriodSerializer(many=False, required=False)
    usage_status = CodeableConceptSerializer(many=False, required=False)
    usage_reason = CodeableConceptSerializer(many=True, required=False)
    adherence = DeviceUsageAdherenceSerializer(many=False, required=False)
    information_source = DeviceUsageInformationSourceReferenceSerializer(
        many=False, required=False
    )
    device = DeviceDeviceDefinitionCodeableReferenceSerializer(
        many=False, required=False
    )
    reason = DeviceUsageReasonCodeableReferenceSerializer(many=True, required=False)
    body_site = BodyStructureCodeableReferenceSerializer(many=False, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceUsage
        exclude = ["created_at", "updated_at"]
