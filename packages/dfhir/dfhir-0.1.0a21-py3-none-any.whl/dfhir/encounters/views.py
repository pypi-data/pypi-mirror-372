"""Encounter views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import EncounterFilter
from .models import (
    DietPreference,
    Encounter,
    EncounterCondition,
    SpecialArrangement,
    SpecialCourtesy,
)
from .serializers import (
    DietPreferenceSerializer,
    EncounterConditionSerializer,
    EncounterSerializer,
    SpecialArrangementSerializer,
    SpecialCourtesySerializer,
)


class EncounterListView(APIView):
    """Encounter List Views."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200, EncounterSerializer(many=True)})
    def get(self, request):
        """Get all encounters."""
        encounter = Encounter.objects.all()
        encounter_filters = EncounterFilter(request.GET, queryset=encounter)
        serializer = EncounterSerializer(encounter_filters.qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=EncounterSerializer, responses={201, EncounterSerializer})
    def post(self, request):
        """Create and encounter."""
        serializer = EncounterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        encounter = serializer.save()
        detailed_serializer = EncounterSerializer(encounter)
        return Response(detailed_serializer.data, status=status.HTTP_201_CREATED)


class EncounterDetailView(APIView):
    """Encounter Serializer Detail View."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get encounter object."""
        try:
            return Encounter.objects.get(pk=pk)
        except Encounter.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200, EncounterSerializer})
    def get(self, request, pk=None):
        """Get an encounter."""
        encounter = self.get_object(pk)
        serializer = EncounterSerializer(encounter)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200, EncounterSerializer})
    def patch(self, request, pk=None):
        """Update and encounter."""
        encounter = self.get_object(pk=pk)
        serializer = EncounterSerializer(encounter, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete and encounter."""
        encounter = self.get_object(pk)
        encounter.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(responses={200, EncounterConditionSerializer(many=True)})
class EncounterConditionListView(ListAPIView):
    """Encounter Condition List View."""

    model = EncounterCondition
    queryset = EncounterCondition.objects.all()
    permission_classes = [AllowAny]


@extend_schema(responses={200, DietPreferenceSerializer(many=True)})
class DietPreferenceListView(ListAPIView):
    """Diet Preference List View."""

    queryset = DietPreference.objects.all()
    permission_classes = [AllowAny]
    serializer_class = DietPreferenceSerializer


@extend_schema(responses={200, SpecialCourtesySerializer(many=True)})
class SpecialCourtesyListView(ListAPIView):
    """Special Preference List View."""

    queryset = SpecialCourtesy.objects.all()
    permission_classes = [AllowAny]
    serializer_class = SpecialCourtesySerializer


@extend_schema(responses={200, SpecialArrangementSerializer(many=True)})
class SpecialArrangementListView(ListAPIView):
    """Encounter Condition List View."""

    queryset = SpecialArrangement.objects.all()
    permission_classes = [AllowAny]
    serializer_class = SpecialArrangementSerializer
