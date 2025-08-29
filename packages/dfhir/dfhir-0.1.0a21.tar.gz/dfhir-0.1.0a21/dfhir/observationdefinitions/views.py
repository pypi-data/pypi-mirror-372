"""observation definitions views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.observationdefinitions.models import ObservationDefinition
from dfhir.observationdefinitions.serializers import ObservationDefinitionSerializer


class ObservationDefinitionListView(APIView):
    """observation definition list view."""

    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: ObservationDefinitionSerializer(many=True)},
    )
    def get(self, request):
        """Get observation definitions."""
        queryset = ObservationDefinition.objects.all()
        serializer = ObservationDefinitionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ObservationDefinitionSerializer,
        responses={201: ObservationDefinitionSerializer},
    )
    def post(self, request):
        """Create observation definition."""
        serializer = ObservationDefinitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ObservationDefinitionDetailView(APIView):
    """observation definition detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get observation definition object."""
        try:
            return ObservationDefinition.objects.get(pk=pk)
        except ObservationDefinition.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ObservationDefinitionSerializer})
    def get(self, request, pk=None):
        """Get observation definition."""
        observation_definition = self.get_object(pk)
        serializer = ObservationDefinitionSerializer(observation_definition)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: ObservationDefinitionSerializer})
    def patch(self, request, pk=None):
        """Update observation definition."""
        observation_definition = self.get_object(pk)
        serializer = ObservationDefinitionSerializer(
            observation_definition, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete observation definition."""
        observation_definition = self.get_object(pk)
        observation_definition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
