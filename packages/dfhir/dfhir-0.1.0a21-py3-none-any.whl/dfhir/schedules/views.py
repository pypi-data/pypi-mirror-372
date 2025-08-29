"""Schedule views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.schedules.models import Schedule
from dfhir.schedules.serializers import ScheduleSerializer

from .filters import ScheduleFilter


class ScheduleListView(APIView):
    """Schedule list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ScheduleSerializer(many=True)})
    def get(self, request):
        """Get schedules."""
        schedules = Schedule.objects.all()
        schedule_filter = ScheduleFilter(request.GET, queryset=schedules)
        serializer = ScheduleSerializer(schedule_filter.qs, many=True)
        return Response(serializer.data)

    @extend_schema(request=ScheduleSerializer, responses={200: ScheduleSerializer})
    def post(self, request):
        """Create a new schedule."""
        serializer = ScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ScheduleDetailView(APIView):
    """Schedule detail view."""

    @extend_schema(responses={200: ScheduleSerializer})
    def get_object(self, pk):
        """Get schedule object."""
        try:
            return Schedule.objects.get(pk=pk)
        except Schedule.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ScheduleSerializer})
    def get(self, request, pk=None):
        """Get schedule."""
        schedule = self.get_object(pk)
        serializer = ScheduleSerializer(schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: ScheduleSerializer})
    def patch(self, request, pk=None):
        """Update schedule."""
        schedule = self.get_object(pk)
        serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete schedule."""
        schedule = self.get_object(pk)
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
