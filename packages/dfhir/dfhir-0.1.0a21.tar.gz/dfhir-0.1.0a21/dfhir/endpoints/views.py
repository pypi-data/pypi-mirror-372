"""Endpoints views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Endpoint
from .serializers import EndpointSerializer


class EndpointListView(APIView):
    """Endpoint List Views."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200, EndpointSerializer(many=True)})
    def get(self, request):
        """Get all endpoints."""
        endpoint = Endpoint.objects.all()
        serializer = EndpointSerializer(endpoint, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=EndpointSerializer, responses={201, EndpointSerializer})
    def post(self, request):
        """Create and endpoint."""
        serializer = EndpointSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        endpoint = serializer.save()
        detailed_serializer = EndpointSerializer(endpoint)
        return Response(detailed_serializer.data, status=status.HTTP_201_CREATED)


class EndpointDetailView(APIView):
    """Endpoint Serializer Detail View."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get endpoint object."""
        try:
            return Endpoint.objects.get(pk=pk)
        except Endpoint.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200, EndpointSerializer})
    def get(self, request, pk):
        """Get an endpoint."""
        endpoint = self.get_object(pk)
        serializer = EndpointSerializer(endpoint)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=EndpointSerializer, responses={200, EndpointSerializer})
    def put(self, request, pk):
        """Update an endpoint."""
        endpoint = self.get_object(pk)
        serializer = EndpointSerializer(endpoint, data=request.data)
        serializer.is_valid(raise_exception=True)
        endpoint = serializer.save()
        detailed_serializer = EndpointSerializer(endpoint)
        return Response(detailed_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204})
    def delete(self, request, pk):
        """Delete an endpoint."""
        endpoint = self.get_object(pk)
        endpoint.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
