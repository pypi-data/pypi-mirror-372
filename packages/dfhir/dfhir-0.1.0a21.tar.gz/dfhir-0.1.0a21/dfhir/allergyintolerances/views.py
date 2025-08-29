"""Allergy intolerances views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AllergyIntolerance
from .serializers import AllergyIntoleranceSerializer


class AllergyIntoleranceListView(APIView):
    """Allergy intolerance list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: AllergyIntoleranceSerializer(many=True)})
    def get(self, request):
        """Get all allergy intolerances."""
        allergy_intolerances = AllergyIntolerance.objects.all()
        serializer = AllergyIntoleranceSerializer(allergy_intolerances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=AllergyIntoleranceSerializer,
        responses={201: AllergyIntoleranceSerializer},
    )
    def post(self, request):
        """Create an allergy intolerance."""
        serializer = AllergyIntoleranceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AllergyIntoleranceDetailView(APIView):
    """Allergy intolerance detail view."""

    def get_object(self, pk):
        """Get an allergy intolerance object."""
        try:
            return AllergyIntolerance.objects.get(pk=pk)
        except AllergyIntolerance.DoesNotExist as error:
            raise Http404 from error

    @extend_schema(responses={200: AllergyIntoleranceSerializer})
    def get(self, request, pk=None):
        """Get an allergy intolerance."""
        allergy_intolerance = self.get_object(pk)
        serializer = AllergyIntoleranceSerializer(allergy_intolerance)
        return Response(serializer.data)

    @extend_schema(
        request=AllergyIntoleranceSerializer,
        responses={200: AllergyIntoleranceSerializer},
    )
    def patch(self, request, pk):
        """Update an allergy intolerance."""
        allergy_intolerance = self.get_object(pk)
        serializer = AllergyIntoleranceSerializer(
            allergy_intolerance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete an allergy intolerance."""
        allergy_intolerance = self.get_object(pk)
        allergy_intolerance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
