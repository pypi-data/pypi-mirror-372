"""Device Definitions views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DeviceDefinition
from .serializers import DeviceDefinitionSerializer


class DeviceDefinitionListCreateView(APIView):
    """Device Definition list create view."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=DeviceDefinitionSerializer, responses={201: DeviceDefinitionSerializer}
    )
    def post(self, request):
        """Create a device definition."""
        serializer = DeviceDefinitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: DeviceDefinitionSerializer(many=True)})
    def get(self, request):
        """Get all device definitions."""
        device_definitions = DeviceDefinition.objects.all()
        serializer = DeviceDefinitionSerializer(device_definitions, many=True)
        return Response(serializer.data)


class DeviceDefinitionDetailView(APIView):
    """Device Definition detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get device definition object."""
        try:
            return DeviceDefinition.objects.get(id=pk)
        except DeviceDefinition.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: DeviceDefinitionSerializer})
    def get(self, request, pk=None):
        """Get device definition detail."""
        device_definition = self.get_object(pk)
        serializer = DeviceDefinitionSerializer(device_definition)
        return Response(serializer.data)

    @extend_schema(
        request=DeviceDefinitionSerializer, responses={200: DeviceDefinitionSerializer}
    )
    def patch(self, request, pk=None):
        """Update device definition."""
        device_definition = self.get_object(pk)
        serializer = DeviceDefinitionSerializer(device_definition, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a device definition."""
        device_definition = self.get_object(pk)
        device_definition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
