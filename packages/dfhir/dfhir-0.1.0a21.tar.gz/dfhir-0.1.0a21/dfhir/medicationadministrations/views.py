"""medication administrations views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.medicationadministrations.models import MedicationAdministration
from dfhir.medicationadministrations.serializers import (
    MedicationAdministrationSerializer,
)


class MedicationAdministrationListView(APIView):
    """medication administration list view."""

    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: MedicationAdministrationSerializer(many=True)},
    )
    def get(self, request):
        """Get."""
        queryset = MedicationAdministration.objects.all()
        serializer = MedicationAdministrationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=MedicationAdministrationSerializer,
        responses={201: MedicationAdministrationSerializer},
    )
    def post(self, request):
        """Post."""
        serializer = MedicationAdministrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MedicationAdministrationDetailView(APIView):
    """medication administration detail view."""

    def get_object(self, pk):
        """Get object."""
        try:
            return MedicationAdministration.objects.get(pk=pk)
        except MedicationAdministration.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: MedicationAdministrationSerializer})
    def get(self, request, pk=None):
        """Get a medication administration by PK."""
        medication_administration = self.get_object(pk)
        serializer = MedicationAdministrationSerializer(medication_administration)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: MedicationAdministrationSerializer})
    def patch(self, request, pk=None):
        """Patch a medication administration by PK."""
        medication_administration = self.get_object(pk)
        serializer = MedicationAdministrationSerializer(
            medication_administration, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete a medication administration by PK."""
        medication_administration = self.get_object(pk)
        medication_administration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
