"""Appointments views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import AppointmentFilter
from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentListView(APIView):
    """Appointment list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: AppointmentSerializer(many=True)})
    def get(self, request):
        """Get all appointments."""
        appointments = Appointment.objects.all()
        appointment_filter = AppointmentFilter(request.GET, queryset=appointments)
        serializer = AppointmentSerializer(appointment_filter.qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=AppointmentSerializer, responses={201: AppointmentSerializer}
    )
    def post(self, request):
        """Create an appointment."""
        serializer = AppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AppointmentDetailView(APIView):
    """Appointment detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get an appointment object."""
        try:
            return Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200, AppointmentSerializer})
    def get(self, request, pk=None):
        """Get an appointment."""
        appointment = self.get_object(pk)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: AppointmentSerializer})
    def patch(self, request, pk=None):
        """Update an appointment."""
        appointment = self.get_object(pk)
        serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete an appointment."""
        appointment = self.get_object(pk)
        appointment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
