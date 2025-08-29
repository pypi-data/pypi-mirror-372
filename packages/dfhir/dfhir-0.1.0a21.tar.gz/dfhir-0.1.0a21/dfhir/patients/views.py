"""Patient views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Patient
from .serializers import PatientSerializer


class PatientListView(APIView):
    """Patient list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: PatientSerializer(many=True)})
    def get(self, request, pk=None):
        """Get all patients."""
        queryset = Patient.objects.all()
        serializer = PatientSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(request=PatientSerializer, responses={200: PatientSerializer})
    def post(self, request):
        """Create a patient."""
        request_data = request.data
        request_data.pop("user", None)

        serializer = PatientSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PatientDetailView(APIView):
    """Patient detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get patient object."""
        try:
            return Patient.objects.get(pk=pk)
        except Patient.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: PatientSerializer})
    def get(self, request, pk=None):
        """Get a patient."""
        queryset = self.get_object(pk)
        serializer = PatientSerializer(queryset)
        return Response(serializer.data)

    @extend_schema(responses={200: PatientSerializer})
    def patch(self, request, pk=None):
        """Update a patient."""
        queryset = self.get_object(pk)
        serializer = PatientSerializer(queryset, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk=None):
        """Delete a patient."""
        patient = self.get_object(pk)
        patient.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
