"""Clinical impression views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ClinicalImpression
from .serializers import ClinicalImpressionSerializer


class ClinicalImpressionListView(APIView):
    """Clinical impression create view."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=ClinicalImpressionSerializer,
        responses={201: ClinicalImpressionSerializer},
    )
    def post(self, request):
        """Create a clinical impression."""
        serializer = ClinicalImpressionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: ClinicalImpressionSerializer})
    def get(self, request):
        """Get all clinical impressions."""
        clinical_impressions = ClinicalImpression.objects.all()
        serializer = ClinicalImpressionSerializer(clinical_impressions, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ClinicalImpressionsDetailView(APIView):
    """Clinical impression detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get clinical impression object."""
        try:
            return ClinicalImpression.objects.get(pk=pk)
        except ClinicalImpression.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ClinicalImpressionSerializer})
    def get(self, request, pk=None):
        """Get a clinical impression."""
        queryset = self.get_object(pk)
        serializer = ClinicalImpressionSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: ClinicalImpressionSerializer})
    def patch(self, request, pk=None):
        """Update a clinical impression."""
        queryset = self.get_object(pk)
        serializer = ClinicalImpressionSerializer(
            queryset, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete a clinical impression."""
        clinical_impression = self.get_object(pk)
        clinical_impression.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
