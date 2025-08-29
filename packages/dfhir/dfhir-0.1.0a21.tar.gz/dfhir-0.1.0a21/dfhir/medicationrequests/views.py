"""medication requests views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.medicationrequests.models import (
    AdditionalIllustration,
    DosageMethod,
    DosageRoute,
    DosageSite,
    MedicationRequest,
    MedicationRequestCategory,
    MedicationRequestMedicationCode,
    MedicationRequestReason,
    MedicationRequestReferenceType,
    ReferenceAsNeededFor,
)
from dfhir.medicationrequests.serializers import (
    AdditionalIllustrationSerializer,
    DosageMethodSerializer,
    DosageRouteSerializer,
    DosageSiteSerializer,
    MediationRequestReferenceTypeSerializer,
    MedicationRequestCategorySerializer,
    MedicationRequestMedicationCodeSerializer,
    MedicationRequestReasonSerializer,
    MedicationRequestSerializer,
    ReferenceAsNeededForSerializer,
)


class MedicationRequestList(APIView):
    """MedicationRequestList."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: MedicationRequestSerializer(many=True)})
    def get(self, request):
        """Get medication requests."""
        medication_requests = MedicationRequest.objects.all()
        serializer = MedicationRequestSerializer(medication_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=MedicationRequestSerializer,
        responses={201: MedicationRequestSerializer},
    )
    def post(self, request):
        """Create medication request."""
        serializer = MedicationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MedicationRequestDetail(APIView):
    """medication request detail."""

    def get_object(self, pk):
        """Get medication request object."""
        try:
            return MedicationRequest.objects.get(pk=pk)
        except MedicationRequest.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: MedicationRequestSerializer})
    def get(self, request, pk=None):
        """Get medication request."""
        medication_request = self.get_object(pk)
        serializer = MedicationRequestSerializer(medication_request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: MedicationRequestSerializer})
    def patch(self, request, pk=None):
        """Update medication request."""
        medication_request = self.get_object(pk)
        serializer = MedicationRequestSerializer(
            medication_request, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete medication request."""
        medication_request = self.get_object(pk)
        medication_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(responses={200: MedicationRequestCategorySerializer(many=True)})
class MedicationRequestCategoryList(ListAPIView):
    """medication request category list."""

    queryset = MedicationRequestCategory.objects.all()
    serializer_class = MedicationRequestCategorySerializer
    permission_classes = [AllowAny]


@extend_schema(responses={200: MedicationRequestReasonSerializer(many=True)})
class MedicationRequestReasonList(ListAPIView):
    """medication request reason list."""

    queryset = MedicationRequestReason.objects.all()
    serializer_class = MedicationRequestReasonSerializer
    permission_classes = [AllowAny]


@extend_schema(responses={200: MedicationRequestMedicationCodeSerializer(many=True)})
class MedicationRequestMedicationCodeList(ListAPIView):
    """medication request medication code list."""

    queryset = MedicationRequestMedicationCode.objects.all()
    serializer_class = MedicationRequestMedicationCodeSerializer
    permission_classes = [AllowAny]


@extend_schema(responses={200: MediationRequestReferenceTypeSerializer(many=True)})
class MediationRequestReferenceTypeList(ListAPIView):
    """medication request reference type list."""

    queryset = MedicationRequestReferenceType.objects.all()
    serializer_class = MediationRequestReferenceTypeSerializer
    permission_classes = [AllowAny]


@extend_schema(responses={200: MedicationRequestSerializer(many=True)})
class AdditionalIllustrationList(ListAPIView):
    """additional illustration list."""

    queryset = AdditionalIllustration.objects.all()
    serializer_class = AdditionalIllustrationSerializer
    permission_classes = [AllowAny]


@extend_schema(responses={200: MedicationRequestSerializer(many=True)})
class DosageSiteList(ListAPIView):
    """dosage site list."""

    queryset = DosageSite.objects.all()
    serializer_class = DosageSiteSerializer
    permission_classes = [AllowAny]


@extend_schema(responses={200: MedicationRequestSerializer(many=True)})
class DosageRouteList(ListAPIView):
    """dosage route list."""

    queryset = DosageRoute.objects.all()
    serializer_class = DosageRouteSerializer
    permission_classes = [AllowAny]


@extend_schema(responses={200: MedicationRequestSerializer(many=True)})
class DosageMethodList(ListAPIView):
    """dosage method list."""

    queryset = DosageMethod.objects.all()
    serializer_class = DosageMethodSerializer
    permission_classes = [AllowAny]


@extend_schema(responses={200: MedicationRequestSerializer(many=True)})
class ReferenceAsNeededForList(ListAPIView):
    """reference as needed for list."""

    queryset = ReferenceAsNeededFor.objects.all()
    serializer_class = ReferenceAsNeededForSerializer
    permission_classes = [AllowAny]
