"""CoverageEligibilityRequests views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CoverageEligibilityRequest
from .serializers import CoverageEligibilityRequestSerializer


class CoverageEligibilityRequestListView(APIView):
    """CoverageEligibilityRequest list create view."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=CoverageEligibilityRequestSerializer,
        responses={201: CoverageEligibilityRequestSerializer},
    )
    def post(self, request):
        """Create a coverage eligibility request."""
        serializer = CoverageEligibilityRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: CoverageEligibilityRequestSerializer(many=True)})
    def get(self, request):
        """Get all coverage eligibility requests."""
        coverage_eligibility_requests = CoverageEligibilityRequest.objects.all()
        serializer = CoverageEligibilityRequestSerializer(
            coverage_eligibility_requests, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CoverageEligibilityRequestDetailView(APIView):
    """CoverageEligibilityRequest detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get coverage eligibility request object."""
        try:
            return CoverageEligibilityRequest.objects.get(id=pk)
        except CoverageEligibilityRequest.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: CoverageEligibilityRequestSerializer})
    def get(self, request, pk=None):
        """Get coverage eligibility request detail."""
        coverage_eligibility_request = self.get_object(pk)
        serializer = CoverageEligibilityRequestSerializer(coverage_eligibility_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=CoverageEligibilityRequestSerializer,
        responses={200: CoverageEligibilityRequestSerializer},
    )
    def patch(self, request, pk=None):
        """Update coverage eligibility request."""
        coverage_eligibility_request = self.get_object(pk)
        serializer = CoverageEligibilityRequestSerializer(
            coverage_eligibility_request, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete coverage eligibility request."""
        coverage_eligibility_request = self.get_object(pk)
        coverage_eligibility_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
