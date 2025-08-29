"""Location views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import LocationFilter
from .models import Location
from .serializers import LocationSerializer


class LocationList(APIView):
    """Location list view."""

    permission_classes = [AllowAny]
    serializer = LocationSerializer
    filter_class = LocationFilter

    @extend_schema(responses={200: LocationSerializer(many=True)}, filters=True)
    def get(self, request):
        """Get locations."""
        locations = Location.objects.all()
        locations_filter = self.filter_class(request.GET, queryset=locations)
        serializer = LocationSerializer(locations_filter.qs, many=True)
        return Response(serializer.data)

    @extend_schema(request=LocationSerializer, responses={200: LocationSerializer})
    def post(self, request):
        """Create location."""
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationDetail(APIView):
    """Location detail view."""

    permission_classes = [AllowAny]
    serializer = LocationSerializer

    def get_object(self, pk):
        """Get location object."""
        try:
            return Location.objects.get(pk=pk)
        except Location.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: LocationSerializer})
    def get(self, request, pk=None):
        """Get location."""
        location = Location.objects.get(pk=pk)
        serializer = self.serializer(location)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: LocationSerializer})
    def patch(self, request, pk=None):
        """Update location."""
        location = Location.objects.get(pk=pk)
        serializer = self.serializer(location, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete location."""
        location = Location.objects.get(pk=pk)
        location.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
