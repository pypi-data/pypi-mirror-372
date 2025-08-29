"""immunization recommendations views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.immunizationrecommendations.models import ImmunizationRecommendation
from dfhir.immunizationrecommendations.serializers import (
    ImmunizationRecommendationSerializer,
)


class ImmunizationRecommendationListView(APIView):
    """immunization recommendation list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ImmunizationRecommendationSerializer(many=True)})
    def get(self, request):
        """Get all objects."""
        queryset = ImmunizationRecommendation.objects.all()
        serializer = ImmunizationRecommendationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ImmunizationRecommendationSerializer,
        responses={201: ImmunizationRecommendationSerializer},
    )
    def post(self, request):
        """Create a new object."""
        serializer = ImmunizationRecommendationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ImmunizationRecommendationDetailView(APIView):
    """immunization recommendation detail view."""

    def get_object(self, pk):
        """Get object by pk."""
        try:
            return ImmunizationRecommendation.objects.get(pk=pk)
        except ImmunizationRecommendation.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ImmunizationRecommendationSerializer})
    def get(self, request, pk):
        """Get object by pk."""
        obj = self.get_object(pk)
        serializer = ImmunizationRecommendationSerializer(obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ImmunizationRecommendationSerializer,
        responses={200: ImmunizationRecommendationSerializer},
    )
    def patch(self, request, pk):
        """Update object by pk."""
        obj = self.get_object(pk)
        serializer = ImmunizationRecommendationSerializer(
            obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete object by pk."""
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
