"""Payment Notices Views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PaymentNotice
from .serializers import PaymentNoticeSerializer


class PaymentNoticeListView(APIView):
    """Payment Notice list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: PaymentNoticeSerializer(many=True)})
    def get(self, request):
        """Get a list of payment notices."""
        payment_notices = PaymentNotice.objects.all()
        serializer = PaymentNoticeSerializer(payment_notices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=PaymentNoticeSerializer, responses={201: PaymentNoticeSerializer}
    )
    def post(self, request):
        """Create a payment notice."""
        serializer = PaymentNoticeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PaymentNoticeDetailView(APIView):
    """Payment Notice detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a payment notice object."""
        try:
            return PaymentNotice.objects.get(pk=pk)
        except PaymentNotice.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: PaymentNoticeSerializer})
    def get(self, request, pk=None):
        """Get a payment notice."""
        payment_notice = self.get_object(pk)
        serializer = PaymentNoticeSerializer(payment_notice)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=PaymentNoticeSerializer, responses={200: PaymentNoticeSerializer}
    )
    def patch(self, request, pk=None):
        """Update a payment notice."""
        payment_notice = self.get_object(pk)
        serializer = PaymentNoticeSerializer(
            payment_notice, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a payment notice."""
        payment_notice = self.get_object(pk)
        payment_notice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
