"""activity definition views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.activitydefinitions.models import ActivityDefinition
from dfhir.activitydefinitions.serializers import ActivityDefinitionSerializer


class ActivityDefinitionListView(APIView):
    """activity definition list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses=ActivityDefinitionSerializer)
    def get(self, request):
        """Get activity definition objects."""
        activity_definitions = ActivityDefinition.objects.all()
        serializer = ActivityDefinitionSerializer(activity_definitions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ActivityDefinitionSerializer, responses=ActivityDefinitionSerializer
    )
    def post(self, request):
        """Create activity definition object."""
        serializer = ActivityDefinitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ActivityDefinitionDetailView(APIView):
    """activity definition detail view."""

    def get_object(self, pk):
        """Get activity definition object."""
        try:
            return ActivityDefinition.objects.get(pk=pk)
        except ActivityDefinition.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses=ActivityDefinitionSerializer)
    def get(self, request, pk):
        """Get activity definition object."""
        activity_definition = self.get_object(pk)
        serializer = ActivityDefinitionSerializer(activity_definition)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ActivityDefinitionSerializer, responses=ActivityDefinitionSerializer
    )
    def patch(self, request, pk):
        """Update activity definition object."""
        activity_definition = self.get_object(pk)
        serializer = ActivityDefinitionSerializer(
            activity_definition, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete activity definition object."""
        activity_definition = self.get_object(pk)
        activity_definition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
