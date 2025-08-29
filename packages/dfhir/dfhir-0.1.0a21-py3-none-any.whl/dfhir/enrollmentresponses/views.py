"""EnrollmentResponses views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EnrollmentResponse
from .serializers import EnrollmentResponseSerializer


class EnrollmentResponseListView(APIView):
    """EnrollmentResponse list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: EnrollmentResponseSerializer(many=True)})
    def get(self, request):
        """Get a list of enrollment responses."""
        enrollment_responses = EnrollmentResponse.objects.all()
        serializer = EnrollmentResponseSerializer(enrollment_responses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=EnrollmentResponseSerializer,
        responses={201: EnrollmentResponseSerializer},
    )
    def post(self, request):
        """Create an enrollment response."""
        serializer = EnrollmentResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EnrollmentResponseDetailView(APIView):
    """EnrollmentResponse detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get an enrollment response object."""
        try:
            return EnrollmentResponse.objects.get(pk=pk)
        except EnrollmentResponse.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: EnrollmentResponseSerializer})
    def get(self, request, pk=None):
        """Get an enrollment response."""
        enrollment_response = self.get_object(pk)
        serializer = EnrollmentResponseSerializer(enrollment_response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=EnrollmentResponseSerializer,
        responses={200: EnrollmentResponseSerializer},
    )
    def patch(self, request, pk=None):
        """Update an enrollment response."""
        enrollment_response = self.get_object(pk)
        serializer = EnrollmentResponseSerializer(
            enrollment_response, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete an enrollment response."""
        enrollment_response = self.get_object(pk)
        enrollment_response.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
