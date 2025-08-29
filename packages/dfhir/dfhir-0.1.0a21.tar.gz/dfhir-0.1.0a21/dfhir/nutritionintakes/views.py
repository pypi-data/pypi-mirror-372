"""nutrition intake views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.nutritionintakes.models import NutritionIntake
from dfhir.nutritionintakes.serializers import NutritionIntakeSerializer


class NutritionIntakeListView(APIView):
    """nutrition intake list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: NutritionIntakeSerializer(many=True)})
    def get(self, request):
        """Get all nutrition intakes."""
        nutrition_intakes = NutritionIntake.objects.all()
        serializer = NutritionIntakeSerializer(nutrition_intakes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=NutritionIntakeSerializer, responses={201: NutritionIntakeSerializer}
    )
    def post(self, request):
        """Create a new nutrition intake."""
        serializer = NutritionIntakeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NutritionIntakeDetailView(APIView):
    """nutrition intake detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get nutrition intake object."""
        try:
            return NutritionIntake.objects.get(pk=pk)
        except NutritionIntake.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: NutritionIntakeSerializer})
    def get(self, request, pk=None):
        """Get a nutrition intake."""
        nutrition_intake = self.get_object(pk)
        serializer = NutritionIntakeSerializer(nutrition_intake)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=NutritionIntakeSerializer, responses={200: NutritionIntakeSerializer}
    )
    def patch(self, request, pk=None):
        """Update a nutrition intake."""
        nutrition_intake = self.get_object(pk)
        serializer = NutritionIntakeSerializer(
            nutrition_intake, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a nutrition intake."""
        nutrition_intake = self.get_object(pk)
        nutrition_intake.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
