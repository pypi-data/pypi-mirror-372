"""Specimen definitions views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import SpecimenDefinition
from .serializers import SpecimenDefinitionSerializer


class SpecimenDefinitionListView(APIView):
    """Specimen Definition List Views."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200, SpecimenDefinitionSerializer(many=True)})
    def get(self, request):
        """Get all specimen definitions."""
        specimen_definitions = SpecimenDefinition.objects.all()
        serializer = SpecimenDefinitionSerializer(specimen_definitions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=SpecimenDefinitionSerializer,
        responses={201, SpecimenDefinitionSerializer},
    )
    def post(self, request):
        """Create a specimen definition."""
        serializer = SpecimenDefinitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SpecimenDefinitionDetailView(APIView):
    """Specimen Definition Detail View."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get specimen definition object."""
        try:
            return SpecimenDefinition.objects.get(pk=pk)
        except SpecimenDefinition.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200, SpecimenDefinitionSerializer})
    def get(self, request, pk=None):
        """Get specimen definition detail."""
        specimen_definition = self.get_object(pk)
        serializer = SpecimenDefinitionSerializer(specimen_definition)
        return Response(serializer.data)

    @extend_schema(
        request=SpecimenDefinitionSerializer,
        responses={200, SpecimenDefinitionSerializer},
    )
    def patch(self, request, pk=None):
        """Update specimen definition."""
        specimen_definition = self.get_object(pk)
        serializer = SpecimenDefinitionSerializer(
            specimen_definition, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={200, SpecimenDefinitionSerializer})
    def delete(self, request, pk=None):
        """Delete specimen definition."""
        specimen_definition = self.get_object(pk)
        specimen_definition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
