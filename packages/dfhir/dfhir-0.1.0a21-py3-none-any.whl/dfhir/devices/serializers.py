"""device serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    ContactPointSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    QuantitySerializer,
    RangeSerializer,
)
from dfhir.devicedefinitions.serializers import DeviceDefinitionReferenceSerializer
from dfhir.endpoints.serializers import EndpointReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer

from .models import (
    Device,
    DeviceCodeableReference,
    DeviceConformsTo,
    DeviceDeviceDefinitionCodeableReference,
    DeviceDeviceDefinitionReference,
    DeviceDeviceMetricReference,
    DeviceName,
    DeviceProperty,
    DeviceReference,
    DeviceUdiCarrier,
    DeviceVersion,
)


class DeviceUdiCarrierSerializer(WritableNestedModelSerializer):
    """Device UDI carrier serializer."""

    class Meta:
        """Meta class."""

        model = DeviceUdiCarrier
        exclude = ["created_at", "updated_at"]


class DeviceNameSerializer(WritableNestedModelSerializer):
    """Device name serializer."""

    type = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceName
        exclude = ["created_at", "updated_at"]


class DeviceVersionSerializer(WritableNestedModelSerializer):
    """Device version serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    component = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceVersion
        exclude = ["created_at", "updated_at"]


class DeviceConformsToSerializer(WritableNestedModelSerializer):
    """Device conforms to serializer."""

    category = CodeableConceptSerializer(many=False, required=False)
    specification = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceConformsTo
        exclude = ["created_at", "updated_at"]


class DevicePropertySerializer(WritableNestedModelSerializer):
    """Device property serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    value_range = RangeSerializer(many=False, required=False)
    value_quantity = QuantitySerializer(many=False, required=False)
    value_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    value_attachment = AttachmentSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceProperty
        exclude = ["created_at", "updated_at"]


class DeviceReferenceSerializer(WritableNestedModelSerializer):
    """Device reference serializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceReference
        exclude = ["created_at", "updated_at"]


class DeviceCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Device codeable reference serializer."""

    concept = CodeableConceptSerializer(many=False, required=False)
    reference = DeviceReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceCodeableReference
        exclude = ["created_at", "updated_at"]


class DeviceSerializer(BaseWritableNestedModelSerializer):
    """Device serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    definition = DeviceDefinitionReferenceSerializer(many=False, required=False)
    udi_carrier = DeviceUdiCarrierSerializer(many=True, required=False)
    availability_status = CodeableConceptSerializer(many=False, required=False)
    biological_source_event = IdentifierSerializer(many=False, required=False)
    name = DeviceNameSerializer(many=True, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    device_version = DeviceVersionSerializer(many=True, required=False)
    conforms_to = DeviceConformsToSerializer(many=True, required=False)
    property = DevicePropertySerializer(many=True, required=False)
    mode = CodeableConceptSerializer(many=False, required=False)
    duration = QuantitySerializer(many=False, required=False)
    owner = OrganizationReferenceSerializer(many=False, required=False)
    contact = ContactPointSerializer(many=True, required=False)
    location = LocationReferenceSerializer(many=False, required=False)
    endpoint = EndpointReferenceSerializer(many=False, required=False)
    gateway = DeviceCodeableReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    safety = CodeableConceptSerializer(many=True, required=False)
    parent = DeviceReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = Device
        exclude = ["created_at", "updated_at"]


class DeviceDeviceMetricReferenceSerializer(BaseReferenceModelSerializer):
    """Device device metric reference serializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDeviceMetricReference
        exclude = ["created_at", "updated_at"]


class DeviceDeviceDefinitionReferenceSerializer(BaseReferenceModelSerializer):
    """Device device definition reference serializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDeviceDefinitionReference
        exclude = ["created_at", "updated_at"]


class DeviceDeviceDefinitionCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Device device definition codeable reference serializer."""

    reference = DeviceDeviceDefinitionReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDeviceDefinitionCodeableReference
        exclude = ["created_at", "updated_at"]
