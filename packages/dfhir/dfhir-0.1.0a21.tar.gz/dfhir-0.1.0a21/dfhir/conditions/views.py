"""Views for the conditions app."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.conditions.models import Condition
from dfhir.conditions.serializers import ConditionSerializer


class ConditionListView(APIView):
    """condition list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ConditionSerializer(many=True)})
    def get(self, request):
        """Get all conditions."""
        conditions = Condition.objects.all()
        serializer = ConditionSerializer(conditions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ConditionSerializer, responses={201: ConditionSerializer})
    def post(self, request):
        """Create a new condition."""
        serializer = ConditionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConditionDetailView(APIView):
    """Condition detail view."""

    def get_object(self, pk):
        """Get condition object."""
        try:
            return Condition.objects.get(pk=pk)
        except Condition.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ConditionSerializer})
    def get(self, request, pk):
        """Get condition."""
        condition = self.get_object(pk)
        serializer = ConditionSerializer(condition)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ConditionSerializer, responses={200: ConditionSerializer})
    def patch(self, request, pk):
        """Update condition."""
        condition = self.get_object(pk)
        serializer = ConditionSerializer(condition, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete condition."""
        condition = self.get_object(pk)
        condition.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
