"""supply delivery views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.supplydeliveries.models import SupplyDelivery
from dfhir.supplydeliveries.serializers import SupplyDeliverySerializer


class SupplyDeliveryListView(APIView):
    """supply delivery list view."""

    permission_classes = (AllowAny,)

    @extend_schema(responses={200: SupplyDeliverySerializer(many=True)})
    def get(self, request):
        """Get supply delivery objects."""
        supply_deliveries = SupplyDeliverySerializer(SupplyDelivery.objects.all())
        serializer = SupplyDeliverySerializer(supply_deliveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=SupplyDeliverySerializer, responses={201: SupplyDeliverySerializer}
    )
    def post(self, request):
        """Create supply delivery object."""
        serializer = SupplyDeliverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SupplyDeliveryDetailedView(APIView):
    """supply delivery detailed view."""

    def get_object(self, pk):
        """Get object method."""
        try:
            return SupplyDelivery.objects.get(pk=pk)
        except SupplyDelivery.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: SupplyDeliverySerializer})
    def get(self, request, pk):
        """Get a supply delivery item."""
        supply_delivery = self.get_object(pk)
        serializer = SupplyDeliverySerializer(supply_delivery)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=SupplyDeliverySerializer, responses={200: SupplyDeliverySerializer}
    )
    def patch(self, request, pk):
        """Update a supply delivery item."""
        supply_delivery = self.get_object(pk)
        serializer = SupplyDeliverySerializer(
            supply_delivery, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete supply delivery item."""
        supply_delivery = self.get_object(pk)
        supply_delivery.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
