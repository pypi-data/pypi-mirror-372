"""inventoru report views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.inventoryreports.models import InventoryReport
from dfhir.inventoryreports.serializer import InventoryReportSerializer


class InventoryReportListView(APIView):
    """inventory report list view."""

    permission_classes = (AllowAny,)

    @extend_schema(responses={200: InventoryReportSerializer(many=True)})
    def get(self, request):
        """Get inventory reports."""
        inventory_reports = InventoryReport.objects.all()
        serializer = InventoryReportSerializer(inventory_reports, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=InventoryReportSerializer, responses={200: InventoryReportSerializer}
    )
    def post(self, request):
        """Post inventory reports."""
        serializer = InventoryReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InventoryReportDetailView(APIView):
    """inventory report detail view."""

    def get_object(self):
        """Get inventory report detail."""
        try:
            return InventoryReport.objects.get(pk=self.kwargs["pk"])
        except InventoryReport.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: InventoryReportSerializer})
    def get(self, request, pk):
        """Get inventory report detail."""
        inventory_report = self.get_object()
        serializer = InventoryReportSerializer(inventory_report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: InventoryReportSerializer})
    def patch(self, request, pk):
        """Patch inventory report detail."""
        inventory_report = self.get_object()
        serializer = InventoryReportSerializer(
            inventory_report, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: None})
    def delete(self, request, pk):
        """Delete inventory report detail."""
        inventory_report = self.get_object()
        inventory_report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
