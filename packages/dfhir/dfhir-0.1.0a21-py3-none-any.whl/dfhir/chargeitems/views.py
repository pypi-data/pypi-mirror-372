"""charge item views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.chargeitems.models import ChargeItem
from dfhir.chargeitems.serializers import ChargeItemSerializer


class ChargeItemListView(APIView):
    """ChargeItem list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ChargeItemSerializer(many=True)})
    def get(self, request):
        """Get all charge items."""
        charge_items = ChargeItem.objects.all()
        serializer = ChargeItemSerializer(charge_items, many=True)
        return Response(serializer.data)

    @extend_schema(request=ChargeItemSerializer, responses={201: ChargeItemSerializer})
    def post(self, request):
        """Create a charge item."""
        serializer = ChargeItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChargeItemDetailView(APIView):
    """ChargeItem detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a charge item object."""
        try:
            return ChargeItem.objects.get(pk=pk)
        except ChargeItem.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ChargeItemSerializer})
    def get(self, request, pk):
        """Get a charge item."""
        charge_item = self.get_object(pk)
        serializer = ChargeItemSerializer(charge_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ChargeItemSerializer, responses={200: ChargeItemSerializer})
    def patch(self, request, pk):
        """Update a charge item."""
        charge_item = self.get_object(pk)
        serializer = ChargeItemSerializer(charge_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete a charge item."""
        charge_item = self.get_object(pk)
        charge_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
