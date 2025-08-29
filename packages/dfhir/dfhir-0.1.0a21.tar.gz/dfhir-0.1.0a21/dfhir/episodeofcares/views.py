"""Episode of Care views."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EpisodeOfCare
from .serializers import EpisodeOfCareSerializer


class EpisodeOfCareListView(APIView):
    """Episode of Care list view."""

    serializer = EpisodeOfCareSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses={200, EpisodeOfCareSerializer(many=True)})
    def get(self, request):
        """Get all episodes of care."""
        episodes_of_care = EpisodeOfCare.objects.all()
        serializer = self.serializer(episodes_of_care, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=EpisodeOfCareSerializer,
        responses={201, EpisodeOfCareSerializer},
    )
    def post(self, request):
        """Create a new episode of care."""
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EpisodeOfCareDetailView(APIView):
    """Episode of Care detail view."""

    serializer = EpisodeOfCareSerializer

    def get_object(self, pk=None):
        """Get episode of care object."""
        try:
            return EpisodeOfCare.objects.get(pk=pk)
        except EpisodeOfCare.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(responses={200, EpisodeOfCareSerializer})
    def get(self, request, pk):
        """Get an episode of care."""
        episode_of_care = self.get_object(pk)
        serializer = self.serializer(episode_of_care)
        return Response(serializer.data)

    @extend_schema(responses={200, EpisodeOfCareSerializer})
    def patch(self, request, pk):
        """Update an episode of care."""
        episode_of_care = self.get_object(pk)
        serializer = self.serializer(episode_of_care, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204})
    def delete(self, request, pk):
        """Delete an episode of care."""
        episode_of_care = self.get_object(pk)
        episode_of_care.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(responses={200, EpisodeOfCareSerializer})
    def put(self, request, pk):
        """Update an episode of care."""
        episode_of_care = self.get_object(pk)
        serializer = self.serializer(episode_of_care, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
