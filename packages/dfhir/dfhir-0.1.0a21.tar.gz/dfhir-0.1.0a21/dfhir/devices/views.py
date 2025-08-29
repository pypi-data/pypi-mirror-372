"""Devices views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Device
from .serializers import DeviceSerializer


class DeviceListView(APIView):
    """Device list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: DeviceSerializer(many=True)})
    def get(self, request):
        """Get all devices."""
        devices = Device.objects.all()
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)

    @extend_schema(request=DeviceSerializer, responses={201: DeviceSerializer})
    def post(self, request):
        """Create a device."""
        serializer = DeviceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeviceDetailView(APIView):
    """Device detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get device object."""
        try:
            return Device.objects.get(pk=pk)
        except Device.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: DeviceSerializer})
    def get(self, request, pk):
        """Get a device."""
        device = self.get_object(pk)
        serializer = DeviceSerializer(device)
        return Response(serializer.data)

    @extend_schema(request=DeviceSerializer, responses={200: DeviceSerializer})
    def put(self, request, pk):
        """Update a device."""
        device = self.get_object(pk)
        serializer = DeviceSerializer(device, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a device."""
        device = self.get_object(pk)
        device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
