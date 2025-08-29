"""transport views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.transports.models import Transport
from dfhir.transports.serializers import TransportSerializer


class TransportListView(APIView):
    """TransportListView."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: TransportSerializer(many=True)})
    def get(self, request):
        """Get."""
        transports = Transport.objects.all()
        serializer = TransportSerializer(transports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=TransportSerializer, responses={201: TransportSerializer})
    def post(self, request):
        """Post."""
        serializer = TransportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransportDetailView(APIView):
    """TransportDetailView."""

    def get_object(self, pk):
        """get_object."""
        try:
            return Transport.objects.get(pk=pk)
        except Transport.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: TransportSerializer})
    def get(self, request, pk):
        """Get."""
        transport = self.get_object(pk)
        serializer = TransportSerializer(transport)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=TransportSerializer, responses={200: TransportSerializer})
    def patch(self, request, pk):
        """Put."""
        transport = self.get_object(pk)
        serializer = TransportSerializer(transport, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete."""
        transport = self.get_object(pk)
        transport.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
