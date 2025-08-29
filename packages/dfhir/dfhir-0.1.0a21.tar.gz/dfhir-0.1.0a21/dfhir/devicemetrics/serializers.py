"""Device metrics Serializer."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    QuantitySerializer,
)
from dfhir.devices.serializers import DeviceReferenceSerializer

from .models import (
    DeviceMetric,
    DeviceMetricCalibration,
)


class DeviceMetricCalibrationSerializer(WritableNestedModelSerializer):
    """Device Metric Calibration Serializer."""

    type = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceMetricCalibration
        exclude = ["created_at", "updated_at"]


class DeviceMetricSerializer(BaseWritableNestedModelSerializer):
    """Device Metric Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    unit = CodeableConceptSerializer(many=False, required=False)
    device = DeviceReferenceSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=False, required=False)
    measurement_frequency = QuantitySerializer(many=False, required=False)
    calibration = DeviceMetricCalibrationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceMetric
        exclude = ["created_at", "updated_at"]
