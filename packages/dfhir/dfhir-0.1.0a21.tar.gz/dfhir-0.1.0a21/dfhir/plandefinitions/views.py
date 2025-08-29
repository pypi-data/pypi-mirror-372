"""Plandefinitions app views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PlanDefinition
from .serializers import PlanDefinitionSerializer


class PlanDefinitionListView(APIView):
    """PlanDefinition list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: PlanDefinitionSerializer(many=True)})
    def get(self, request):
        """Get a list of plan definitions."""
        plan_definitions = PlanDefinition.objects.all()
        serializer = PlanDefinitionSerializer(plan_definitions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=PlanDefinitionSerializer, responses={201: PlanDefinitionSerializer}
    )
    def post(self, request):
        """Create a plan definition."""
        serializer = PlanDefinitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PlanDefinitionDetailView(APIView):
    """PlanDefinition detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a plan definition object."""
        try:
            return PlanDefinition.objects.get(pk=pk)
        except PlanDefinition.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: PlanDefinitionSerializer})
    def get(self, request, pk=None):
        """Get a plan definition."""
        plan_definition = self.get_object(pk)
        serializer = PlanDefinitionSerializer(plan_definition)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=PlanDefinitionSerializer, responses={200: PlanDefinitionSerializer}
    )
    def patch(self, request, pk=None):
        """Update a plan definition."""
        plan_definition = self.get_object(pk)
        serializer = PlanDefinitionSerializer(
            plan_definition, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a plan definition."""
        plan_definition = self.get_object(pk)
        plan_definition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
