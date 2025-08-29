"""specimens views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.specimens.models import Specimen
from dfhir.specimens.serializers import SpecimenSerializer


class SpecimenListView(APIView):
    """Specimen list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: SpecimenSerializer(many=True)})
    def get(self, request):
        """Get specimens."""
        specimens = Specimen.objects.all()
        serializer = SpecimenSerializer(specimens, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=SpecimenSerializer, responses={201: SpecimenSerializer})
    def post(self, request):
        """Create a new specimen."""
        serializer = SpecimenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SpecimenDetailView(APIView):
    """specimen detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get specimen object."""
        try:
            return Specimen.objects.get(pk=pk)
        except Specimen.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: SpecimenSerializer})
    def get(self, request, pk=None):
        """Get specimen."""
        specimen = self.get_object(pk)
        serializer = SpecimenSerializer(specimen)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=SpecimenSerializer, responses={200: SpecimenSerializer})
    def patch(self, request, pk=None):
        """Update specimen."""
        specimen = self.get_object(pk)
        serializer = SpecimenSerializer(specimen, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete specimen."""
        specimen = self.get_object(pk)
        specimen.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
