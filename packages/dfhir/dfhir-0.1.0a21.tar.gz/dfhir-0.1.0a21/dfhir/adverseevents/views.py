"""Adverse events views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AdverseEvent
from .serializers import AdverseEventSerializer


class AdverseEventListView(APIView):
    """Adverse event list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: AdverseEventSerializer(many=True)})
    def get(self, request):
        """Get a list of adverse events."""
        adverse_events = AdverseEvent.objects.all()
        serializer = AdverseEventSerializer(adverse_events, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=AdverseEventSerializer, responses={201: AdverseEventSerializer}
    )
    def post(self, request):
        """Create an adverse event."""
        serializer = AdverseEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AdverseEventDetailView(APIView):
    """Adverse event detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get an adverse event object."""
        try:
            return AdverseEvent.objects.get(pk=pk)
        except AdverseEvent.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: AdverseEventSerializer})
    def get(self, request, pk):
        """Get an adverse event."""
        adverse_event = self.get_object(pk)
        serializer = AdverseEventSerializer(adverse_event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=AdverseEventSerializer, responses={200: AdverseEventSerializer}
    )
    def patch(self, request, pk):
        """Update an adverse event."""
        adverse_event = self.get_object(pk)
        serializer = AdverseEventSerializer(
            adverse_event, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete an adverse event."""
        adverse_event = self.get_object(pk)
        adverse_event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
