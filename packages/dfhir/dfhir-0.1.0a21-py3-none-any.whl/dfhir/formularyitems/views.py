"""formulary item views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.formularyitems.models import FormularyItem
from dfhir.formularyitems.serializers import FormularyItemSerializer


class FormularyItemListView(APIView):
    """formulary item list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: FormularyItemSerializer(many=True)})
    def get(self, request):
        """Get request."""
        formulary_items = FormularyItem.objects.all()
        serializer = FormularyItemSerializer(formulary_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=FormularyItemSerializer, responses={200: FormularyItemSerializer}
    )
    def post(self, request):
        """Post request."""
        serializer = FormularyItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FormularyItemDetailView(APIView):
    """formulary item detail view."""

    def get_object(self, pk):
        """Get object."""
        try:
            return FormularyItem.objects.get(pk=pk)
        except FormularyItem.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: FormularyItemSerializer})
    def get(self, request, pk):
        """Get request."""
        formulary_item = self.get_object(pk)
        serializer = FormularyItemSerializer(formulary_item)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=FormularyItemSerializer, responses={200: FormularyItemSerializer}
    )
    def patch(self, request, pk):
        """Patch request."""
        formulary_item = self.get_object(pk)
        serializer = FormularyItemSerializer(
            formulary_item, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete request."""
        formulary_item = self.get_object(pk)
        formulary_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
