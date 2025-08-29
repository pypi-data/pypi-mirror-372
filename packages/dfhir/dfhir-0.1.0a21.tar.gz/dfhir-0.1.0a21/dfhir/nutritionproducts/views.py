"""Nutrition products views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import NutritionProduct
from .serializers import NutritionProductSerializer


class NutritionProductListView(APIView):
    """Nutrition Product List View."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: NutritionProductSerializer(many=True)})
    def get(self, request):
        """Get all nutrition products."""
        nutrition_products = NutritionProduct.objects.all()
        serializer = NutritionProductSerializer(nutrition_products, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=NutritionProductSerializer, responses={201: NutritionProductSerializer}
    )
    def post(self, request):
        """Create a nutrition product."""
        serializer = NutritionProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NutritionProductDetailView(APIView):
    """Nutrition Product Detail View."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get nutrition product object."""
        try:
            return NutritionProduct.objects.get(id=pk)
        except NutritionProduct.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: NutritionProductSerializer})
    def get(self, request, pk=None):
        """Get nutrition product detail."""
        nutrition_product = self.get_object(pk)
        serializer = NutritionProductSerializer(nutrition_product)
        return Response(serializer.data)

    @extend_schema(
        request=NutritionProductSerializer, responses={200: NutritionProductSerializer}
    )
    def patch(self, request, pk=None):
        """Update nutrition product."""
        nutrition_product = self.get_object(pk)
        serializer = NutritionProductSerializer(nutrition_product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a nutrition product."""
        nutrition_product = self.get_object(pk)
        nutrition_product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
