"""care plan views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CarePlan
from .serializers import CarePlanSerializer


class CarePlanListView(APIView):
    """CarePlan list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: CarePlanSerializer(many=True)})
    def get(self, request):
        """Get a list of care plans."""
        care_plans = CarePlan.objects.all()
        serializer = CarePlanSerializer(care_plans, many=True)
        return Response(serializer.data)

    @extend_schema(request=CarePlanSerializer, responses={201: CarePlanSerializer})
    def post(self, request):
        """Create a care plan."""
        serializer = CarePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CarePlanDetailView(APIView):
    """CarePlan detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a care plan object."""
        try:
            return CarePlan.objects.get(pk=pk)
        except CarePlan.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: CarePlanSerializer})
    def get(self, request, pk=None):
        """Get a care plan."""
        care_plan = self.get_object(pk)
        serializer = CarePlanSerializer(care_plan)
        return Response(serializer.data)

    @extend_schema(request=CarePlanSerializer, responses={200: CarePlanSerializer})
    def patch(self, request, pk=None):
        """Update a care plan."""
        care_plan = self.get_object(pk)
        serializer = CarePlanSerializer(care_plan, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a care plan."""
        care_plan = self.get_object(pk)
        care_plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
