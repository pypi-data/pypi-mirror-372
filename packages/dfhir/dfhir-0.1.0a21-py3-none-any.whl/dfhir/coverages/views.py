"""Coverage views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Coverage
from .serializers import CoverageSerializer


class CoverageListView(APIView):
    """Coverage list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: CoverageSerializer(many=True)})
    def get(self, request):
        """Get a list of coverages."""
        coverages = Coverage.objects.all()
        serializer = CoverageSerializer(coverages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=CoverageSerializer, responses={201: CoverageSerializer})
    def post(self, request):
        """Create a coverage."""
        serializer = CoverageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CoverageDetailView(APIView):
    """Coverage detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a coverage object."""
        try:
            return Coverage.objects.get(pk=pk)
        except Coverage.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: CoverageSerializer})
    def get(self, request, pk):
        """Get a coverage."""
        coverage = self.get_object(pk)
        serializer = CoverageSerializer(coverage)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=CoverageSerializer, responses={200: CoverageSerializer})
    def patch(self, request, pk):
        """Update a coverage."""
        coverage = self.get_object(pk)
        serializer = CoverageSerializer(coverage, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a coverage."""
        coverage = self.get_object(pk)
        coverage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
