"""immunization app views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.immunizations.models import Immunization
from dfhir.immunizations.serializers import ImmunizationSerializer


class ImmunizationListView(APIView):
    """Immunization list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ImmunizationSerializer(many=True)})
    def get(self, request):
        """Get a list of immunizations."""
        immunizations = Immunization.objects.all()
        serializer = ImmunizationSerializer(immunizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ImmunizationSerializer, responses={201: ImmunizationSerializer}
    )
    def post(self, request):
        """Create a new immunization."""
        serializer = ImmunizationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ImmunizationDetailView(APIView):
    """Immunization detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get an immunization object."""
        try:
            return Immunization.objects.get(pk=pk)
        except Immunization.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ImmunizationSerializer})
    def get(self, request, pk):
        """Get an immunization."""
        immunization = self.get_object(pk)
        serializer = ImmunizationSerializer(immunization)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ImmunizationSerializer, responses={200: ImmunizationSerializer}
    )
    def patch(self, request, pk):
        """Update an immunization."""
        immunization = self.get_object(pk)
        serializer = ImmunizationSerializer(
            immunization, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete an immunization."""
        immunization = self.get_object(pk)
        immunization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
