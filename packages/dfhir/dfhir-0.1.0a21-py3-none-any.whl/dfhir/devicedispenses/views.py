"""Devicedispenses app views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DeviceDispense
from .serializers import DeviceDispenseSerializer


class DeviceDispenseListView(APIView):
    """DeviceDispense list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: DeviceDispenseSerializer(many=True)})
    def get(self, request):
        """Get a list of device dispenses."""
        device_dispenses = DeviceDispense.objects.all()
        serializer = DeviceDispenseSerializer(device_dispenses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DeviceDispenseSerializer, responses={201: DeviceDispenseSerializer}
    )
    def post(self, request):
        """Create a device dispense."""
        serializer = DeviceDispenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeviceDispenseDetailView(APIView):
    """DeviceDispense detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a device dispense object."""
        try:
            return DeviceDispense.objects.get(pk=pk)
        except DeviceDispense.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: DeviceDispenseSerializer})
    def get(self, request, pk=None):
        """Get a device dispense."""
        device_dispense = self.get_object(pk)
        serializer = DeviceDispenseSerializer(device_dispense)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DeviceDispenseSerializer, responses={200: DeviceDispenseSerializer}
    )
    def patch(self, request, pk=None):
        """Update a device dispense."""
        device_dispense = self.get_object(pk)
        serializer = DeviceDispenseSerializer(
            device_dispense, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a device dispense."""
        device_dispense = self.get_object(pk)
        device_dispense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
