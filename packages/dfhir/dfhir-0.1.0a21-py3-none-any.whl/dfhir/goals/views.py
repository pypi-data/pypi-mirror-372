"""Goals views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Goal
from .serializers import GoalSerializer


class GoalListView(APIView):
    """Goal list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: GoalSerializer(many=True)})
    def get(self, request):
        """Get all goals."""
        goals = Goal.objects.all()
        serializer = GoalSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=GoalSerializer, responses={201: GoalSerializer})
    def post(self, request):
        """Create goal."""
        serializer = GoalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GoalDetailView(APIView):
    """Goal detail view."""

    def get_object(self, pk):
        """Get a goal object by ID."""
        try:
            return Goal.objects.get(pk=pk)
        except Goal.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: GoalSerializer})
    def get(self, request, pk):
        """Get a goal."""
        goal = self.get_object(pk)
        serializer = GoalSerializer(goal)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=GoalSerializer, responses={200: GoalSerializer})
    def patch(self, request, pk):
        """Update a goal."""
        goal = self.get_object(pk)
        serializer = GoalSerializer(goal, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a goal."""
        goal = self.get_object(pk)
        goal.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
