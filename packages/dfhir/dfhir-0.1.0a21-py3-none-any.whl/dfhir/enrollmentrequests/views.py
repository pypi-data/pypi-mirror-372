"""Enrollment Requests Views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EnrollmentRequest
from .serializers import EnrollmentRequestSerializer


class EnrollmentRequestListView(APIView):
    """Enrollment Request list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: EnrollmentRequestSerializer(many=True)})
    def get(self, request):
        """Get all enrollment requests."""
        enrollment_requests = EnrollmentRequest.objects.all()
        serializer = EnrollmentRequestSerializer(enrollment_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=EnrollmentRequestSerializer,
        responses={201: EnrollmentRequestSerializer},
    )
    def post(self, request):
        """Create an enrollment request."""
        serializer = EnrollmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EnrollmentRequestDetailView(APIView):
    """Enrollment Request detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get enrollment request object."""
        try:
            return EnrollmentRequest.objects.get(id=pk)
        except EnrollmentRequest.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: EnrollmentRequestSerializer})
    def get(self, request, pk=None):
        """Get enrollment request detail."""
        enrollment_request = self.get_object(pk)
        serializer = EnrollmentRequestSerializer(enrollment_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=EnrollmentRequestSerializer,
        responses={200: EnrollmentRequestSerializer},
    )
    def patch(self, request, pk=None):
        """Update enrollment request."""
        enrollment_request = self.get_object(pk)
        serializer = EnrollmentRequestSerializer(
            enrollment_request, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete enrollment request."""
        enrollment_request = self.get_object(pk)
        enrollment_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
