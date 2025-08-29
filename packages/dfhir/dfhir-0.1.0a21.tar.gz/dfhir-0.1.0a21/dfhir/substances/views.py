"""Substances views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Substance
from .serializers import SubstanceSerializer


class SubstanceListView(APIView):
    """Substance list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: SubstanceSerializer(many=True)})
    def get(self, request):
        """Get substance list."""
        substances = Substance.objects.all()
        serializer = SubstanceSerializer(substances, many=True)
        return Response(serializer.data)

    @extend_schema(request=SubstanceSerializer, responses={201: SubstanceSerializer})
    def post(self, request):
        """Create a substance."""
        serializer = SubstanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SubstanceDetailView(APIView):
    """Substance detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get substance object."""
        try:
            return Substance.objects.get(pk=pk)
        except Substance.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: SubstanceSerializer})
    def get(self, request, pk=None):
        """Get substance detail."""
        substance = self.get_object(pk)
        serializer = SubstanceSerializer(substance)
        return Response(serializer.data)

    @extend_schema(request=SubstanceSerializer, responses={200: SubstanceSerializer})
    def patch(self, request, pk=None):
        """Update substance."""
        substance = self.get_object(pk)
        serializer = SubstanceSerializer(substance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a substance."""
        substance = self.get_object(pk)
        substance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
