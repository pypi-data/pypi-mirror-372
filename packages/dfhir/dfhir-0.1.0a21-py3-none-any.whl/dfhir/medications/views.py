"""medications views file."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.medications.models import (
    Medication,
    MedicationCodes,
    MedicationDoseForm,
    MedicationIngredientItem,
)
from dfhir.medications.serializers import (
    MedicationCodesSerializer,
    MedicationDoseFormSerializer,
    MedicationIngredientItemSerializer,
    MedicationSerializer,
)


class MedicationsList(APIView):
    """medications list API view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: MedicationSerializer(many=True)})
    def get(self, request):
        """Get medications list."""
        medications = Medication.objects.all()
        serializer = MedicationSerializer(medications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=MedicationSerializer, responses={201: MedicationSerializer})
    def post(self, request):
        """Create medication."""
        serializer = MedicationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MedicationDetail(APIView):
    """medication detail API view."""

    def get_object(self, pk):
        """Get medication object."""
        try:
            return Medication.objects.get(pk=pk)
        except Medication.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: MedicationSerializer})
    def get(self, request, pk=None):
        """Get medication."""
        medication = self.get_object(pk)
        serializer = MedicationSerializer(medication)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: MedicationSerializer})
    def patch(self, request, pk=None):
        """Update medication."""
        medication = self.get_object(pk)
        serializer = MedicationSerializer(medication, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete medication."""
        medication = self.get_object(pk)
        medication.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(responses={200: MedicationSerializer(many=True)})
class MedicationCodesList(ListAPIView):
    """medication codes list API view."""

    queryset = MedicationCodes.objects.all()
    serializer_class = MedicationCodesSerializer
    permission_classes = [AllowAny]


@extend_schema(responses={200: MedicationSerializer(many=True)})
class MedicationDoseFormList(ListAPIView):
    """medication dose form list API view."""

    queryset = MedicationDoseForm.objects.all()
    serializer_class = MedicationDoseFormSerializer
    permission_classes = [AllowAny]


@extend_schema(responses={200: MedicationSerializer(many=True)})
class MedicationIngredientItemList(ListAPIView):
    """medication ingredient item list API view."""

    queryset = MedicationIngredientItem.objects.all()
    serializer_class = MedicationIngredientItemSerializer
    permission_classes = [AllowAny]
