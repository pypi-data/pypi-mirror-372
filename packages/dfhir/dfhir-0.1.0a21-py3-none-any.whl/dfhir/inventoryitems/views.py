"""inventory item views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.inventoryitems.models import InventoryItem
from dfhir.inventoryitems.serializers import InventoryItemSerializer


class InventoryItemListView(APIView):
    """inventory item list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: InventoryItemSerializer(many=True)})
    def get(self, request):
        """List inventory items."""
        queryset = InventoryItem.objects.all()
        serializer = InventoryItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=InventoryItemSerializer, responses={201: InventoryItemSerializer}
    )
    def post(self, request):
        """Create inventory item."""
        serializer = InventoryItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InventoryItemDetailView(APIView):
    """inventory item detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get inventory item object."""
        try:
            return InventoryItem.objects.get(pk=pk)
        except InventoryItem.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: InventoryItemSerializer})
    def get(self, request, pk=None):
        """Retrieve inventory item."""
        inventory_item = self.get_object(pk)
        serializer = InventoryItemSerializer(inventory_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: InventoryItemSerializer})
    def patch(self, request, pk=None):
        """Update inventory item."""
        inventory_item = self.get_object(pk)
        serializer = InventoryItemSerializer(
            inventory_item, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete inventory item."""
        inventory_item = self.get_object(pk)
        inventory_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
