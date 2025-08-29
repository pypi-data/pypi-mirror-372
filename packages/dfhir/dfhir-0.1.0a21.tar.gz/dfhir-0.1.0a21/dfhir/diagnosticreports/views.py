"""diagnostic reports views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.diagnosticreports.models import (
    ConclusionCode,
    DiagnosticCategory,
    DiagnosticReport,
    DiagnosticReportCode,
)
from dfhir.diagnosticreports.serializers import (
    ConclusionCodeSerializer,
    DiagnosticCategorySerializer,
    DiagnosticReportCodeSerializer,
    DiagnosticReportSerializer,
)


class DiagnosticReportListView(APIView):
    """diagnostic report list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: DiagnosticReportSerializer(many=True)})
    def get(self, request):
        """Get all diagnostic reports."""
        diagnostic_reports = DiagnosticReport.objects.all()
        serializer = DiagnosticReportSerializer(diagnostic_reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=DiagnosticReportSerializer, responses={201: DiagnosticReportSerializer}
    )
    def post(self, request):
        """Create a diagnostic report."""
        serializer = DiagnosticReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DiagnosticReportDetailView(APIView):
    """diagnostic report detail view."""

    def get_object(self, pk):
        """Get a diagnostic report object."""
        try:
            return DiagnosticReport.objects.get(pk=pk)
        except DiagnosticReport.DoesNotExist as error:
            raise Http404 from error

    @extend_schema(responses={200: DiagnosticReportSerializer})
    def get(self, request, pk=None):
        """Get a diagnostic report."""
        diagnostic_report = self.get_object(pk)
        serializer = DiagnosticReportSerializer(diagnostic_report)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200, DiagnosticReportSerializer})
    def patch(self, request, pk=None):
        """Update a diagnostic report."""
        diagnostic_report = self.get_object(pk)
        serializer = DiagnosticReportSerializer(
            diagnostic_report, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete a diagnostic report."""
        diagnostic_report = self.get_object(pk)
        diagnostic_report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(responses={200: DiagnosticReportCodeSerializer})
class DiagnosticReportCodeListView(ListAPIView):
    """diagnostic report code list view."""

    serializer_class = DiagnosticReportCodeSerializer
    permission_classes = [AllowAny]
    queryset = DiagnosticReportCode.objects.all()


@extend_schema(responses={200: DiagnosticCategorySerializer})
class DiagnosticCategoryListView(ListAPIView):
    """diagnostic category list view."""

    serializer_class = DiagnosticCategorySerializer
    permission_classes = [AllowAny]
    queryset = DiagnosticCategory.objects.all()


@extend_schema(responses={200: ConclusionCodeSerializer})
class ConclusionCodeListView(ListAPIView):
    """conclusion code list view."""

    serializer_class = ConclusionCodeSerializer
    permission_classes = [AllowAny]
    queryset = ConclusionCode.objects.all()
