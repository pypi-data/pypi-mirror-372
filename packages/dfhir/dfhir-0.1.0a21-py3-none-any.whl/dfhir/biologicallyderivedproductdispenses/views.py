"""biologically derived product dispense views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.biologicallyderivedproductdispenses.models import (
    BiologicallyDerivedProductDispense,
)
from dfhir.biologicallyderivedproductdispenses.serializers import (
    BiologicallyDerivedProductDispenseSerializer,
)


class BiologicallyDerivedProductDispenseListView(APIView):
    """biologically derived product dispense list view."""

    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: BiologicallyDerivedProductDispenseSerializer(many=True)}
    )
    def get(self, request):
        """Get a list of biologically derived product dispenses."""
        biologically_derived_product_dispenses = (
            BiologicallyDerivedProductDispense.objects.all()
        )
        serializer = BiologicallyDerivedProductDispenseSerializer(
            biologically_derived_product_dispenses, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=BiologicallyDerivedProductDispenseSerializer,
        responses={201: BiologicallyDerivedProductDispenseSerializer},
    )
    def post(self, request):
        """Create a biologically derived product dispense."""
        serializer = BiologicallyDerivedProductDispenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BiologicallyDerivedProductDispenseDetailView(APIView):
    """biologically derived product dispense detail view."""

    def get_object(self, pk):
        """Get biologically derived product dispense object."""
        try:
            return BiologicallyDerivedProductDispense.objects.get(pk=pk)
        except BiologicallyDerivedProductDispense.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: BiologicallyDerivedProductDispenseSerializer})
    def get(self, request, pk=None):
        """Get a biologically derived product dispense."""
        biologically_derived_product_dispense = self.get_object(pk)
        serializer = BiologicallyDerivedProductDispenseSerializer(
            biologically_derived_product_dispense
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=BiologicallyDerivedProductDispenseSerializer,
        responses={200: BiologicallyDerivedProductDispenseSerializer},
    )
    def patch(self, request, pk=None):
        """Update a biologically derived product dispense."""
        biologically_derived_product_dispense = self.get_object(pk)
        serializer = BiologicallyDerivedProductDispenseSerializer(
            biologically_derived_product_dispense, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a biologically derived product dispense."""
        biologically_derived_product_dispense = self.get_object(pk)
        biologically_derived_product_dispense.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
