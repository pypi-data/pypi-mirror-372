"""Invoices views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Invoice
from .serializers import InvoiceSerializer


class InvoiceListView(APIView):
    """Invoice list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: InvoiceSerializer(many=True)})
    def get(self, request):
        """Get a list of invoices."""
        invoices = Invoice.objects.all()
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=InvoiceSerializer, responses={201: InvoiceSerializer})
    def post(self, request):
        """Create an invoice."""
        serializer = InvoiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InvoiceDetailView(APIView):
    """Invoice detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get an invoice object."""
        try:
            return Invoice.objects.get(pk=pk)
        except Invoice.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: InvoiceSerializer})
    def get(self, request, pk=None):
        """Get an invoice."""
        invoice = self.get_object(pk)
        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=InvoiceSerializer, responses={200: InvoiceSerializer})
    def patch(self, request, pk=None):
        """Update an invoice."""
        invoice = self.get_object(pk)
        serializer = InvoiceSerializer(invoice, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete an invoice."""
        invoice = self.get_object(pk)
        invoice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
