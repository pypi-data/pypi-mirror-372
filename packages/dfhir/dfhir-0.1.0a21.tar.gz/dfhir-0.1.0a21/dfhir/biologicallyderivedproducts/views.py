"""Biologically Derived Products views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BiologicallyDerivedProduct
from .serializers import BiologicallyDerivedProductSerializer


class BiologicallyDerivedProductListView(APIView):
    """Biologically Derived Product list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: BiologicallyDerivedProductSerializer(many=True)})
    def get(self, request):
        """Get biologically derived product list."""
        biologicallyderivedproducts = BiologicallyDerivedProduct.objects.all()
        serializer = BiologicallyDerivedProductSerializer(
            biologicallyderivedproducts, many=True
        )
        return Response(serializer.data)

    @extend_schema(
        request=BiologicallyDerivedProductSerializer,
        responses={201: BiologicallyDerivedProductSerializer},
    )
    def post(self, request):
        """Create a biologically derived product."""
        serializer = BiologicallyDerivedProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BiologicallyDerivedProductDetailView(APIView):
    """Biologically Derived Product detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get biologically derived product object."""
        try:
            return BiologicallyDerivedProduct.objects.get(pk=pk)
        except BiologicallyDerivedProduct.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: BiologicallyDerivedProductSerializer})
    def get(self, request, pk=None):
        """Get biologically derived product detail."""
        queryset = self.get_object(pk)
        serializer = BiologicallyDerivedProductSerializer(queryset)
        return Response(serializer.data)

    @extend_schema(
        request=BiologicallyDerivedProductSerializer,
        responses={200: BiologicallyDerivedProductSerializer},
    )
    def patch(self, request, pk=None):
        """Update biologically derived product."""
        queryset = self.get_object(pk)
        serializer = BiologicallyDerivedProductSerializer(queryset, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a biologically derived product."""
        biologically_derived_product = self.get_object(pk)
        biologically_derived_product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
