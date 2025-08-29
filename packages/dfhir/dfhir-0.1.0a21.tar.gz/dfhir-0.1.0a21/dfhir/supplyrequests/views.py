"""supply requests views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.supplyrequests.models import SupplyRequest
from dfhir.supplyrequests.serializers import SupplyRequestSerializer


class SupplyRequestListView(APIView):
    """supply request list view."""

    permission_classes = (AllowAny,)

    @extend_schema(responses={200: SupplyRequestSerializer(many=True)})
    def get(self, request):
        """Get supply request objects."""
        supply_requests = SupplyRequest.objects.all()
        serializer = SupplyRequestSerializer(supply_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=SupplyRequestSerializer, responses={201: SupplyRequestSerializer}
    )
    def post(self, request):
        """Create supply request object."""
        serializer = SupplyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SupplyRequestDetailView(APIView):
    """supply request detailed view."""

    def get_object(self, pk):
        """Get supply request object by pk."""
        try:
            return SupplyRequest.objects.get(pk=pk)
        except SupplyRequest.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: SupplyRequestSerializer})
    def get(self, request, pk):
        """Get supply request object by pk."""
        supply_request = self.get_object(pk)
        serializer = SupplyRequestSerializer(supply_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: SupplyRequestSerializer})
    def patch(self, request, pk):
        """Updated a supply request object."""
        supply_request = self.get_object(pk)
        serializer = SupplyRequestSerializer(
            supply_request, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a supply request object."""
        supply_request = self.get_object(pk)
        supply_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
