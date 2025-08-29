"""Detected issues views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DetectedIssue
from .serializers import DetectedIssueSerializer


class DetectedIssueListView(APIView):
    """Detected issue list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: DetectedIssueSerializer(many=True)})
    def get(self, request):
        """Get a list of detected issues."""
        detected_issues = DetectedIssue.objects.all()
        serializer = DetectedIssueSerializer(detected_issues, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=DetectedIssueSerializer, responses={201: DetectedIssueSerializer}
    )
    def post(self, request):
        """Create a detected issue."""
        serializer = DetectedIssueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DetectedIssueDetailView(APIView):
    """Detected issue detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a detected issue object."""
        try:
            return DetectedIssue.objects.get(pk=pk)
        except DetectedIssue.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: DetectedIssueSerializer})
    def get(self, request, pk):
        """Get a detected issue."""
        detected_issue = self.get_object(pk)
        serializer = DetectedIssueSerializer(detected_issue)
        return Response(serializer.data)

    @extend_schema(
        request=DetectedIssueSerializer, responses={200: DetectedIssueSerializer}
    )
    def patch(self, request, pk):
        """Update a detected issue."""
        detected_issue = self.get_object(pk)
        serializer = DetectedIssueSerializer(detected_issue, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a detected issue."""
        detected_issue = self.get_object(pk)
        detected_issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
