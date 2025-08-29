"""medication dispenses views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.medicationdispenses.models import MedicationDispense
from dfhir.medicationdispenses.serializers import MedicationDispenseSerializer


class MedicationDispenseListView(APIView):
    """Medication dispense list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: MedicationDispenseSerializer})
    def get(self, request):
        """List all medication dispenses."""
        queryset = MedicationDispense.objects.all()
        serializer = MedicationDispenseSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=MedicationDispenseSerializer,
        responses={201: MedicationDispenseSerializer},
    )
    def post(self, request):
        """Create a medication dispense."""
        serializer = MedicationDispenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MedicationDispenseDetailView(APIView):
    """Medication dispense detail view."""

    def get_object(self, pk):
        """Get object method."""
        try:
            return MedicationDispense.objects.get(pk=pk)
        except MedicationDispense.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: MedicationDispenseSerializer})
    def get(self, request, pk=None):
        """Retrieve a medication dispense."""
        medication_dispense = self.get_object(pk)
        serializer = MedicationDispenseSerializer(medication_dispense)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request={200, MedicationDispenseSerializer})
    def patch(self, request, pk):
        """Update a medication dispense."""
        medication_dispense = self.get_object(pk)
        serializer = MedicationDispenseSerializer(
            medication_dispense, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete a medication dispense."""
        medication_dispense = self.get_object(pk)
        medication_dispense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
