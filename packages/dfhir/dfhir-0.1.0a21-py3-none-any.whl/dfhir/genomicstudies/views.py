"""genomic study views."""

# Create your views here.
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.genomicstudies.models import GenomicStudy
from dfhir.genomicstudies.serializers import GenomicStudySerializer


class GenomicStudyListView(APIView):
    """GenomicStudy list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: GenomicStudySerializer(many=True)})
    def get(self, request):
        """Get a list of genomic studies."""
        genomic_studies = GenomicStudy.objects.all()
        serializer = GenomicStudySerializer(genomic_studies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=GenomicStudySerializer, responses={201: GenomicStudySerializer}
    )
    def post(self, request):
        """Create a new genomic study."""
        serializer = GenomicStudySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GenomicStudyDetailView(APIView):
    """genomic study detail view."""

    def get_object(self, pk):
        """Get genomic study object."""
        try:
            return GenomicStudy.objects.get(pk=pk)
        except GenomicStudy.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: GenomicStudySerializer})
    def get(self, request, pk):
        """Get a genomic study."""
        genomic_study = self.get_object(pk)
        serializer = GenomicStudySerializer(genomic_study)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=GenomicStudySerializer, responses={200: GenomicStudySerializer}
    )
    def patch(self, request, pk):
        """Update a genomic study."""
        genomic_study = self.get_object(pk)
        serializer = GenomicStudySerializer(
            genomic_study, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a genomic study."""
        genomic_study = self.get_object(pk)
        genomic_study.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
