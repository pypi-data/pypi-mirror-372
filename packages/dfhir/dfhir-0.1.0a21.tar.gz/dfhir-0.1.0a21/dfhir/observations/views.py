"""observation views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Observation,
)
from .serializers import (
    ObservationSerializer,
)


class ObservationListView(APIView):
    """observation list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200, ObservationSerializer(many=True)})
    def get(self, request):
        """Get all observations."""
        observation = Observation.objects.all()
        serializer = ObservationSerializer(observation, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ObservationSerializer, responses={201, ObservationSerializer}
    )
    def post(self, request):
        """Create observation."""
        serializer = ObservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ObservationDetailView(APIView):
    """observation detail view."""

    def get_object(self, pk):
        """Get an observation object by ID."""
        try:
            return Observation.objects.get(pk=pk)
        except Observation.DoesNotExist as error:
            raise Http404 from error

    @extend_schema(responses={200, ObservationSerializer})
    def get(self, request, pk=None):
        """Get an observation."""
        observation = self.get_object(pk)
        serializer = ObservationSerializer(observation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200, ObservationSerializer})
    def patch(self, request, pk):
        """Patch an observation."""
        observation = self.get_object(pk)
        serializer = ObservationSerializer(observation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete an observation."""
        observation = self.get_object(pk)
        observation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
