"""Deviceassociations app views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DeviceAssociation
from .serializers import DeviceAssociationSerializer


class DeviceAssociationListView(APIView):
    """DeviceAssociation list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: DeviceAssociationSerializer(many=True)})
    def get(self, request):
        """Get a list of device associations."""
        device_associations = DeviceAssociation.objects.all()
        serializer = DeviceAssociationSerializer(device_associations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DeviceAssociationSerializer,
        responses={201: DeviceAssociationSerializer},
    )
    def post(self, request):
        """Create a device association."""
        serializer = DeviceAssociationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeviceAssociationDetailView(APIView):
    """DeviceAssociation detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a device association object."""
        try:
            return DeviceAssociation.objects.get(pk=pk)
        except DeviceAssociation.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: DeviceAssociationSerializer})
    def get(self, request, pk=None):
        """Get a device association."""
        device_association = self.get_object(pk)
        serializer = DeviceAssociationSerializer(device_association)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DeviceAssociationSerializer,
        responses={200: DeviceAssociationSerializer},
    )
    def patch(self, request, pk=None):
        """Update a device association."""
        device_association = self.get_object(pk)
        serializer = DeviceAssociationSerializer(
            device_association, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a device association."""
        device_association = self.get_object(pk)
        device_association.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
