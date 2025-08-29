"""imaging study views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.imagingstudies.models import ImagingStudy
from dfhir.imagingstudies.serializers import ImagingStudySerializer


class ImagingStudyListView(APIView):
    """imaging Study list view."""

    permission_classes = (AllowAny,)

    @extend_schema(responses={200: ImagingStudySerializer(many=True)})
    def get(self, request):
        """Get imaging study list."""
        imaging_studies = ImagingStudy.objects.all()
        serializer = ImagingStudySerializer(imaging_studies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ImagingStudySerializer, responses={201: ImagingStudySerializer}
    )
    def post(self, request):
        """Create a new imaging study."""
        serializer = ImagingStudySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ImagingStudyDetailView(APIView):
    """imaging study detail view."""

    permission_classes = (AllowAny,)

    def get_object(self, pk):
        """Get imaging study detail."""
        try:
            return ImagingStudy.objects.get(pk=pk)
        except ImagingStudy.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ImagingStudySerializer})
    def get(self, request, pk):
        """Get imaging study detail."""
        imaging_study = self.get_object(pk)
        serializer = ImagingStudySerializer(imaging_study)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: ImagingStudySerializer})
    def patch(self, request, pk):
        """Update imaging study detail."""
        imaging_study = self.get_object(pk)
        serializer = ImagingStudySerializer(
            imaging_study, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: ImagingStudySerializer})
    def delete(self, request, pk):
        """Delete imaging study detail."""
        imaging_study = self.get_object(pk)
        imaging_study.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
