"""medication knowledge views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.medicationknowledges.models import MedicationKnowledge
from dfhir.medicationknowledges.serializers import MedicationKnowledgeSerializer


class MedicationKnowledgeListView(APIView):
    """MedicationKnowledge list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: MedicationKnowledgeSerializer(many=True)})
    def get(self, request):
        """Get a list of medication knowledge."""
        medication_knowledges = MedicationKnowledge.objects.all()
        serializer = MedicationKnowledgeSerializer(medication_knowledges, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=MedicationKnowledgeSerializer,
        responses={201: MedicationKnowledgeSerializer},
    )
    def post(self, request):
        """Create a medication knowledge."""
        serializer = MedicationKnowledgeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MedicationKnowledgeDetailView(APIView):
    """medication knowledge detail view."""

    def get_object(self, pk):
        """Get medication knowledge object."""
        try:
            return MedicationKnowledge.objects.get(pk=pk)
        except MedicationKnowledge.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: MedicationKnowledgeSerializer})
    def get(self, request, pk=None):
        """Get a medication knowledge."""
        medication_knowledge = self.get_object(pk)
        serializer = MedicationKnowledgeSerializer(medication_knowledge)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=MedicationKnowledgeSerializer,
        responses={200: MedicationKnowledgeSerializer},
    )
    def patch(self, request, pk=None):
        """Update a medication knowledge."""
        medication_knowledge = self.get_object(pk)
        serializer = MedicationKnowledgeSerializer(
            medication_knowledge, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a medication knowledge."""
        medication_knowledge = self.get_object(pk)
        medication_knowledge.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
