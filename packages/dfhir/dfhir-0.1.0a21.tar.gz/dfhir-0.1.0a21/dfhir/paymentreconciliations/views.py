"""payment reconciliations views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.paymentreconciliations.models import PaymentReconciliation
from dfhir.paymentreconciliations.serializers import (
    PaymentReconciliationSerializer,
)


class PaymentReconciliationListView(APIView):
    """Payment reconciliation list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: PaymentReconciliationSerializer(many=True)})
    def get(self, request):
        """Get all payment reconciliations."""
        payment_reconciliations = PaymentReconciliation.objects.all()
        serializer = PaymentReconciliationSerializer(payment_reconciliations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=PaymentReconciliationSerializer,
        responses={201: PaymentReconciliationSerializer},
    )
    def post(self, request):
        """Create a payment reconciliation."""
        serializer = PaymentReconciliationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentReconciliationDetailView(APIView):
    """Payment reconciliation detail view."""

    def get_object(self, pk):
        """Get payment reconciliation object."""
        try:
            return PaymentReconciliation.objects.get(pk=pk)
        except PaymentReconciliation.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: PaymentReconciliationSerializer})
    def get(self, request, pk):
        """Get a payment reconciliation."""
        payment_reconciliation = self.get_object(pk)
        serializer = PaymentReconciliationSerializer(payment_reconciliation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=PaymentReconciliationSerializer,
        responses={200: PaymentReconciliationSerializer},
    )
    def patch(self, request, pk):
        """Update a payment reconciliation."""
        payment_reconciliation = self.get_object(pk)
        serializer = PaymentReconciliationSerializer(
            payment_reconciliation, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a payment reconciliation."""
        payment_reconciliation = self.get_object(pk)
        payment_reconciliation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
