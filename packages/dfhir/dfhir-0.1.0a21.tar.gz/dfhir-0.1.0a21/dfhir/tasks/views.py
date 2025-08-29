"""task views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.tasks.models import Task
from dfhir.tasks.serializers import TaskSerializer


class TaskListView(APIView):
    """task list view."""

    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: TaskSerializer(many=True)},
    )
    def get(self, request):
        """Get all tasks."""
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=TaskSerializer, responses={201: TaskSerializer})
    def post(self, request):
        """Create a task."""
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    """task detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get task object."""
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(
        responses={200: TaskSerializer},
    )
    def get(self, request, pk):
        """Get task."""
        task = self.get_object(pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=TaskSerializer,
        responses={200: TaskSerializer},
    )
    def patch(self, request, pk):
        """Update task."""
        task = self.get_object(pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={204: None},
    )
    def delete(self, request, pk):
        """Delete task."""
        task = self.get_object(pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
