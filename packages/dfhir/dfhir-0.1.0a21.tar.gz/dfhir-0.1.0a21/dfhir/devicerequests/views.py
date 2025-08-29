"""Devicerequests app views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DeviceRequest
from .serializers import DeviceRequestSerializer


class DeviceRequestListView(APIView):
    """DeviceRequest list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: DeviceRequestSerializer(many=True)})
    def get(self, request):
        """Get a list of device requests."""
        device_requests = DeviceRequest.objects.all()
        serializer = DeviceRequestSerializer(device_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DeviceRequestSerializer, responses={201: DeviceRequestSerializer}
    )
    def post(self, request):
        """Create a device request."""
        serializer = DeviceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeviceRequestDetailView(APIView):
    """Device request detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a care plan object."""
        try:
            return DeviceRequest.objects.get(pk=pk)
        except DeviceRequest.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: DeviceRequestSerializer})
    def get(self, request, pk=None):
        """Get a care plan."""
        device_request = self.get_object(pk)
        serializer = DeviceRequestSerializer(device_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DeviceRequestSerializer, responses={200: DeviceRequestSerializer}
    )
    def patch(self, request, pk=None):
        """Update a care plan."""
        device_request = self.get_object(pk)
        serializer = DeviceRequestSerializer(
            device_request, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a care plan."""
        device_request = self.get_object(pk)
        device_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
