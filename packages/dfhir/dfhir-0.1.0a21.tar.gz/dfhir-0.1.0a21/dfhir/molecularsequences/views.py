"""molecular sequences views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.molecularsequences.models import MolecularSequence
from dfhir.molecularsequences.serializers import MolecularSequenceSerializer


class MolecularSequenceListView(APIView):
    """MolecularSequence list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: MolecularSequenceSerializer(many=True)})
    def get(self, request):
        """Get molecular sequences."""
        molecular_sequences = MolecularSequence.objects.all()
        serializer = MolecularSequenceSerializer(molecular_sequences, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=MolecularSequenceSerializer,
        responses={201: MolecularSequenceSerializer},
    )
    def post(self, request):
        """Create a molecular sequence."""
        serializer = MolecularSequenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MolecularSequenceDetailView(APIView):
    """molecular sequence detail view."""

    def get_object(self, pk):
        """Get a molecular sequence object."""
        try:
            return MolecularSequence.objects.get(pk=pk)
        except MolecularSequence.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: MolecularSequenceSerializer})
    def get(self, request, pk):
        """Get a molecular sequence."""
        molecular_sequence = self.get_object(pk)
        serializer = MolecularSequenceSerializer(molecular_sequence)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=MolecularSequenceSerializer,
        responses={200: MolecularSequenceSerializer},
    )
    def patch(self, request, pk):
        """Update a molecular sequence."""
        molecular_sequence = self.get_object(pk)
        serializer = MolecularSequenceSerializer(
            molecular_sequence, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a molecular sequence."""
        molecular_sequence = self.get_object(pk)
        molecular_sequence.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
