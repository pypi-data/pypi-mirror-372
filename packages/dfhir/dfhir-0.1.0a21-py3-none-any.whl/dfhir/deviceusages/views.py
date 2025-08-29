"""DeviceUsages views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DeviceUsage
from .serializers import DeviceUsageSerializer


class DeviceUsageListView(APIView):
    """DeviceUsage list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: DeviceUsageSerializer(many=True)})
    def get(self, request):
        """Get a list of device usages."""
        device_usages = DeviceUsage.objects.all()
        serializer = DeviceUsageSerializer(device_usages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DeviceUsageSerializer, responses={201: DeviceUsageSerializer}
    )
    def post(self, request):
        """Create a device usage."""
        serializer = DeviceUsageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeviceUsageDetailView(APIView):
    """DeviceUsage detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a device usage object."""
        try:
            return DeviceUsage.objects.get(pk=pk)
        except DeviceUsage.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: DeviceUsageSerializer})
    def get(self, request, pk=None):
        """Get a device usage."""
        device_usage = self.get_object(pk)
        serializer = DeviceUsageSerializer(device_usage)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DeviceUsageSerializer, responses={200: DeviceUsageSerializer}
    )
    def patch(self, request, pk=None):
        """Update a device usage."""
        device_usage = self.get_object(pk)
        serializer = DeviceUsageSerializer(
            device_usage, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a device usage."""
        device_usage = self.get_object(pk)
        device_usage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
