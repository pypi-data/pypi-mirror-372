"""Appointment responses views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AppointmentResponse
from .serializers import AppointmentResponseSerializer


class AppointmentResponseListView(APIView):
    """Appointment response list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: AppointmentResponseSerializer(many=True)})
    def get(self, request):
        """Get all appointment responses."""
        appointment_responses = AppointmentResponse.objects.all()
        serializer = AppointmentResponseSerializer(appointment_responses, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=AppointmentResponseSerializer,
        responses={201: AppointmentResponseSerializer},
    )
    def post(self, request):
        """Create an appointment response."""
        serializer = AppointmentResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AppointmentResponseDetailView(APIView):
    """Appointment response detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get appointment response object."""
        try:
            return AppointmentResponse.objects.get(id=pk)
        except AppointmentResponse.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: AppointmentResponseSerializer})
    def get(self, request, pk=None):
        """Get appointment response detail."""
        appointment_response = self.get_object(pk)
        serializer = AppointmentResponseSerializer(appointment_response)
        return Response(serializer.data)

    @extend_schema(
        request=AppointmentResponseSerializer,
        responses={200: AppointmentResponseSerializer},
    )
    def patch(self, request, pk=None):
        """Update appointment response."""
        appointment_response = self.get_object(pk)
        serializer = AppointmentResponseSerializer(
            appointment_response, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete an appointment response."""
        appointment_response = self.get_object(pk)
        appointment_response.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
