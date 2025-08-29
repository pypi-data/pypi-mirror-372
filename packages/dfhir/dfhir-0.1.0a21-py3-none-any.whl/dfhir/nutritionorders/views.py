"""nutrition orders views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.nutritionorders.models import NutritionOrder
from dfhir.nutritionorders.serializers import NutritionOrderSerializer


class NutritionOrderListView(APIView):
    """nutrition order list API view."""

    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: NutritionOrderSerializer(many=True)},
    )
    def get(self, request):
        """Get method."""
        nutrition_orders = NutritionOrder.objects.all()
        serializer = NutritionOrderSerializer(nutrition_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=NutritionOrderSerializer, responses={201: NutritionOrderSerializer}
    )
    def post(self, request):
        """Create nutrition order object."""
        serializer = NutritionOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NutritionOrderDetailView(APIView):
    """nutrition order detail API view."""

    def get_object(self, pk):
        """Get nutrition order object."""
        try:
            return NutritionOrder.objects.get(pk=pk)
        except NutritionOrder.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: NutritionOrderSerializer})
    def get(self, request, pk):
        """Get method."""
        nutrition_order = self.get_object(pk)
        serializer = NutritionOrderSerializer(nutrition_order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: NutritionOrder})
    def patch(self, request, pk):
        """Update nutrition order object."""
        nutrition_order = self.get_object(pk)
        serializer = NutritionOrderSerializer(
            nutrition_order, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete nutrition order object."""
        nutrition_order = self.get_object(pk)
        nutrition_order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
