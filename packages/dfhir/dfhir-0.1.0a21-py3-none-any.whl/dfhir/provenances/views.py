"""provenances views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.provenances.models import Provenance
from dfhir.provenances.serializers import ProvenanceSerializer


class ProvenanceListView(APIView):
    """Provenance list view."""

    permission_classes = [AllowAny]
    serializer_class = ProvenanceSerializer

    @extend_schema(responses={200: ProvenanceSerializer(many=True)})
    def get(self, request):
        """Get all provenances."""
        provenances = Provenance.objects.all()
        serializer = self.serializer_class(provenances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ProvenanceSerializer, responses={201: ProvenanceSerializer})
    def post(self, request):
        """Create a new provenance."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProvenanceDetailView(APIView):
    """Provenance detail view."""

    permission_classes = [AllowAny]
    serializer_class = ProvenanceSerializer

    def get_object(self, pk):
        """Get a provenance object."""
        try:
            return Provenance.objects.get(pk=pk)
        except Provenance.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ProvenanceSerializer})
    def get(self, request, pk):
        """Get a provenance by ID."""
        provenance = self.get_object(pk)
        serializer = self.serializer_class(provenance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ProvenanceSerializer, responses={200: ProvenanceSerializer})
    def patch(self, request, pk):
        """Update a provenance by ID."""
        provenance = self.get_object(pk)
        serializer = self.serializer_class(provenance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a provenance by ID."""
        provenance = self.get_object(pk)
        provenance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
