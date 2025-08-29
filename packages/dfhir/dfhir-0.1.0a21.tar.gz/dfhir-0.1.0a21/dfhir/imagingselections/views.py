"""image selection views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.imagingselections.models import ImagingSelection
from dfhir.imagingselections.serializers import ImagingSelectionSerializer


class ImagingSelectionListView(APIView):
    """ImagingSelection list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ImagingSelectionSerializer(many=True)})
    def get(self, request):
        """Get a list of imaging selections."""
        imaging_selections = ImagingSelection.objects.all()
        serializer = ImagingSelectionSerializer(imaging_selections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ImagingSelectionSerializer, responses={201: ImagingSelectionSerializer}
    )
    def post(self, request):
        """Create an imaging selection."""
        serializer = ImagingSelectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ImagingSelectionDetailView(APIView):
    """imaging selection detail view."""

    def get_object(self, pk):
        """Get imaging selection object."""
        try:
            return ImagingSelection.objects.get(pk=pk)
        except ImagingSelection.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ImagingSelectionSerializer})
    def get(self, request, pk=None):
        """Get an imaging selection."""
        imaging_selection = self.get_object(pk)
        serializer = ImagingSelectionSerializer(imaging_selection)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ImagingSelectionSerializer, responses={200: ImagingSelectionSerializer}
    )
    def patch(self, request, pk=None):
        """Update an imaging selection."""
        imaging_selection = self.get_object(pk)
        serializer = ImagingSelectionSerializer(
            imaging_selection, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete an imaging selection."""
        imaging_selection = self.get_object(pk)
        imaging_selection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
