"""ClaimResponses views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ClaimResponse
from .serializers import ClaimResponseSerializer


class ClaimResponseListView(APIView):
    """ClaimResponse list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ClaimResponseSerializer(many=True)})
    def get(self, request):
        """Get a list of claim responses."""
        claim_responses = ClaimResponse.objects.all()
        serializer = ClaimResponseSerializer(claim_responses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ClaimResponseSerializer, responses={201: ClaimResponseSerializer}
    )
    def post(self, request):
        """Create a claim response."""
        serializer = ClaimResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClaimResponseDetailView(APIView):
    """ClaimResponse detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a claim response object."""
        try:
            return ClaimResponse.objects.get(pk=pk)
        except ClaimResponse.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ClaimResponseSerializer})
    def get(self, request, pk=None):
        """Get a claim response."""
        claim_response = self.get_object(pk)
        serializer = ClaimResponseSerializer(claim_response)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ClaimResponseSerializer, responses={200: ClaimResponseSerializer}
    )
    def patch(self, request, pk=None):
        """Update a claim response."""
        claim_response = self.get_object(pk)
        serializer = ClaimResponseSerializer(
            claim_response, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a claim response."""
        claim_response = self.get_object(pk)
        claim_response.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
