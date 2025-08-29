"""Device Metric Calibration model."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DeviceMetric
from .serializers import DeviceMetricSerializer


class DeviceMetricListView(APIView):
    """Device Metric list view."""

    serializer = DeviceMetricSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses={200, DeviceMetricSerializer(many=True)})
    def get(self, request):
        """Get all device metrics."""
        device_metrics = DeviceMetric.objects.all()
        serializer = self.serializer(device_metrics, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=DeviceMetricSerializer,
        responses={201, DeviceMetricSerializer},
    )
    def post(self, request):
        """Create a new device metric."""
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceMetricDetailView(APIView):
    """Device Metric detail view."""

    serializer = DeviceMetricSerializer

    def get_object(self, pk=None):
        """Get device metric object."""
        try:
            return DeviceMetric.objects.get(pk=pk)
        except DeviceMetric.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(responses={200, DeviceMetricSerializer})
    def get(self, request, pk):
        """Get a device metric."""
        device_metric = self.get_object(pk)
        serializer = self.serializer(device_metric)
        return Response(serializer.data)

    @extend_schema(responses={200, DeviceMetricSerializer})
    def patch(self, request, pk):
        """Update a device metric."""
        device_metric = self.get_object(pk)
        serializer = self.serializer(device_metric, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a device metric."""
        device_metric = self.get_object(pk)
        device_metric.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
