"""service requests views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    AsNeeded,
    BodySite,
    Parameter,
    ProcedureCodes,
    ProcedureReason,
    Reference,
    ServiceRequest,
    ServiceRequestCategory,
)
from .serializers import (
    AsNeededSerializer,
    BodySiteSerializer,
    ParameterSerializer,
    ProcedureCodeSerializer,
    ProcedureReasonSerializer,
    ReferenceSerializer,
    ServiceRequestCategorySerializer,
    ServiceRequestSerializer,
)


class ServiceRequestListView(APIView):
    """service request list views."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200, ServiceRequestSerializer(many=True)})
    def get(self, request):
        """Get all service requests."""
        service_request = ServiceRequest.objects.all()
        serializer = ServiceRequestSerializer(service_request, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ServiceRequestSerializer, responses={201, ServiceRequestSerializer}
    )
    def post(self, request):
        """Service request create view."""
        serializer = ServiceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ServiceRequestDetailView(APIView):
    """service request detail views."""

    def get_object(self, pk):
        """Get object function."""
        try:
            return ServiceRequest.objects.get(pk=pk)
        except ServiceRequest.DoesNotExist as error:
            raise Http404 from error

    @extend_schema(responses={200, ServiceRequestSerializer})
    def get(self, request, pk=None):
        """Service request retrieve view."""
        service_request = self.get_object(pk)
        serializer = ServiceRequestSerializer(service_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200, ServiceRequestSerializer})
    def patch(self, request, pk=None):
        """Service request update view."""
        service_request = self.get_object(pk)
        serializer = ServiceRequestSerializer(
            service_request, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Service reequest delete view."""
        service_request = self.get_object(pk)
        service_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(responses={200, ParameterSerializer})
class ParameterListView(ListAPIView):
    """parameter list view."""

    serializer_class = ParameterSerializer
    permission_classes = [AllowAny]
    queryset = Parameter.objects.all()


@extend_schema(responses={200, ReferenceSerializer})
class ReferenceListView(ListAPIView):
    """reference list view."""

    serializer_class = ReferenceSerializer
    permission_classes = [AllowAny]
    queryset = Reference.objects.all()


@extend_schema(responses={200, ServiceRequestCategorySerializer})
class ServiceRequestCategoryListView(ListAPIView):
    """service request list view."""

    serializer_class = ServiceRequestCategorySerializer
    permission_classes = [AllowAny]
    queryset = ServiceRequestCategory.objects.all()


@extend_schema(responses={200, AsNeededSerializer})
class AsNeededListView(ListAPIView):
    """as needed list view."""

    permission_classes = [AllowAny]
    serializer_class = AsNeededSerializer
    queryset = AsNeeded.objects.all()


@extend_schema(responses={200, ProcedureReasonSerializer})
class ProcedureReasonListView(ListAPIView):
    """procedure reason list view."""

    serializer_class = ProcedureReasonSerializer
    permission_classes = [AllowAny]
    queryset = ProcedureReason.objects.all()


@extend_schema(responses={200, BodySiteSerializer})
class BodySiteListView(ListAPIView):
    """body site list view."""

    permission_classes = [AllowAny]
    serializer_class = BodySiteSerializer
    queryset = BodySite.objects.all()


@extend_schema(responses={200, ProcedureCodeSerializer})
class ProcedureCodesListView(ListAPIView):
    """procedure codes list view."""

    permission_classes = [AllowAny]
    serializer_class = ProcedureCodeSerializer
    queryset = ProcedureCodes.objects.all()
