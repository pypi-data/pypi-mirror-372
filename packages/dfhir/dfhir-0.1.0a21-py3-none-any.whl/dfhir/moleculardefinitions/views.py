"""molecular definitions views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.moleculardefinitions.models import MolecularDefinition
from dfhir.moleculardefinitions.serializers import MolecularDefinitionSerializer


class MolecularDefinitionListView(APIView):
    """molecular definitions list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: MolecularDefinitionSerializer(many=True)})
    def get(self, request):
        """Get molecular definitions."""
        molecular_definitions = MolecularDefinition.objects.all()
        serializer = MolecularDefinitionSerializer(molecular_definitions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=MolecularDefinitionSerializer,
        responses={201: MolecularDefinitionSerializer},
    )
    def post(self, request):
        """Create a new molecular definition."""
        serializer = MolecularDefinitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MolecularDefinitionDetailView(APIView):
    """molecular definitions detail view."""

    def get_object(self, pk):
        """Get molecular definition object."""
        try:
            return MolecularDefinition.objects.get(pk=pk)
        except MolecularDefinition.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: MolecularDefinitionSerializer})
    def get(self, request, pk=None):
        """Get molecular definition."""
        molecular_definition = self.get_object(pk)
        serializer = MolecularDefinitionSerializer(molecular_definition)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: MolecularDefinitionSerializer})
    def patch(self, request, pk=None):
        """Update molecular definition."""
        molecular_definition = self.get_object(pk)
        serializer = MolecularDefinitionSerializer(
            molecular_definition, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete molecular definition."""
        molecular_definition = self.get_object(pk)
        molecular_definition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
