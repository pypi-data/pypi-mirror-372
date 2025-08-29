"""Vision prescription views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import VisionPrescription
from .serializers import VisionPrescriptionSerializer


class VisionPrescriptionListView(APIView):
    """Vision prescription list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: VisionPrescriptionSerializer(many=True)})
    def get(self, request):
        """Get vision prescriptions."""
        vision_prescriptions = VisionPrescription.objects.all()
        serializer = VisionPrescriptionSerializer(vision_prescriptions, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=VisionPrescriptionSerializer,
        responses={201: VisionPrescriptionSerializer},
    )
    def post(self, request):
        """Create a vision prescription."""
        serializer = VisionPrescriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VisionPrescriptionDetailView(APIView):
    """Vision prescription detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get vision prescription object."""
        try:
            return VisionPrescription.objects.get(pk=pk)
        except VisionPrescription.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: VisionPrescriptionSerializer})
    def get(self, request, pk=None):
        """Get a vision prescription."""
        queryset = self.get_object(pk)
        serializer = VisionPrescriptionSerializer(queryset)
        return Response(serializer.data)

    @extend_schema(responses={200: VisionPrescriptionSerializer})
    def patch(self, request, pk=None):
        """Update a vision prescription."""
        queryset = self.get_object(pk)
        serializer = VisionPrescriptionSerializer(
            queryset, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk=None):
        """Delete a vision prescription."""
        vision_prescription = self.get_object(pk)
        vision_prescription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
