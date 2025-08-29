"""Healthcare services views."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.base.models import ServiceType

from .models import ClinicalSpecialty, HealthcareService, ServiceCategory
from .serializers import (
    ClinicalSpecialtySerializer,
    HealthcareServiceSerializer,
    ServiceCategorySerializer,
    ServiceTypeSerializer,
)


class HealthcareServiceListView(APIView):
    """Healthcare Service list view."""

    serializer = HealthcareServiceSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses={200, HealthcareServiceSerializer(many=True)})
    def get(self, request):
        """Get all healthcare services."""
        healthcare_services = HealthcareService.objects.all()
        serializer = self.serializer(healthcare_services, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=HealthcareServiceSerializer,
        responses={201, HealthcareServiceSerializer},
    )
    def post(self, request):
        """Create a new healthcare service."""
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthcareServiceDetailView(APIView):
    """Healthcare Service detail view."""

    serializer = HealthcareServiceSerializer

    def get_object(self, pk=None):
        """Get healthcare service object."""
        try:
            return HealthcareService.objects.get(pk=pk)
        except HealthcareService.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(responses={200, HealthcareServiceSerializer})
    def get(self, request, pk):
        """Get a healthcare service."""
        healthcare_service = self.get_object(pk)
        serializer = self.serializer(healthcare_service)
        return Response(serializer.data)

    @extend_schema(responses={200, HealthcareServiceSerializer})
    def patch(self, request, pk):
        """Update a healthcare service."""
        healthcare_service = self.get_object(pk)
        serializer = self.serializer(
            healthcare_service, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete a healthcare service."""
        healthcare_service = self.get_object(pk)
        healthcare_service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(responses={200, ServiceCategorySerializer(many=True)})
class ServiceCategoryListView(ListAPIView):
    """Service Category list view."""

    serializer_class = ServiceCategorySerializer
    queryset = ServiceCategory.objects.all()
    permission_classes = [AllowAny]


@extend_schema(responses={200, ClinicalSpecialtySerializer(many=True)})
class ClinicalSpecialtyValuesetListView(ListAPIView):
    """Clinical Specialty Valueset list view."""

    serializer_class = ClinicalSpecialtySerializer
    queryset = ClinicalSpecialty.objects.all()
    permission_classes = [AllowAny]


@extend_schema(responses={200, ServiceTypeSerializer(many=True)})
class ServiceTypeListView(ListAPIView):
    """Service Type list view."""

    serializer_class = ServiceTypeSerializer
    queryset = ServiceType.objects.all()
    permission_classes = [AllowAny]
