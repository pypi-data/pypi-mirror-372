"""Coverage Eligibility Responses views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CoverageEligibilityResponse
from .serializers import CoverageEligibilityResponseSerializer


class CoverageEligibilityResponseListView(APIView):
    """Coverage Eligibility Response list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: CoverageEligibilityResponseSerializer(many=True)})
    def get(self, request):
        """Get all coverage eligibility responses."""
        coverage_eligibility_responses = CoverageEligibilityResponse.objects.all()
        serializer = CoverageEligibilityResponseSerializer(
            coverage_eligibility_responses, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CoverageEligibilityResponseSerializer,
        responses={201: CoverageEligibilityResponseSerializer},
    )
    def post(self, request):
        """Create a coverage eligibility response."""
        serializer = CoverageEligibilityResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CoverageEligibilityResponseDetailView(APIView):
    """Coverage Eligibility Response detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get coverage eligibility response object."""
        try:
            return CoverageEligibilityResponse.objects.get(id=pk)
        except CoverageEligibilityResponse.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: CoverageEligibilityResponseSerializer})
    def get(self, request, pk=None):
        """Get coverage eligibility response detail."""
        coverage_eligibility_response = self.get_object(pk)
        serializer = CoverageEligibilityResponseSerializer(
            coverage_eligibility_response
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CoverageEligibilityResponseSerializer,
        responses={200: CoverageEligibilityResponseSerializer},
    )
    def patch(self, request, pk=None):
        """Update coverage eligibility response."""
        coverage_eligibility_response = self.get_object(pk)
        serializer = CoverageEligibilityResponseSerializer(
            coverage_eligibility_response, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete coverage eligibility response."""
        coverage_eligibility_response = self.get_object(pk)
        coverage_eligibility_response.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
