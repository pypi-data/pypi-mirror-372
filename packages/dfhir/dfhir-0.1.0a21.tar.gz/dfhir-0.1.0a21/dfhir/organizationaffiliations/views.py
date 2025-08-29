"""organization affiliation views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.organizationaffiliations.models import OrganizationAffiliation
from dfhir.organizationaffiliations.serializers import (
    OrganizationAffiliationSerializer,
)


class OrganizationAffiliationListview(APIView):
    """organization affiliation list view."""

    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: OrganizationAffiliationSerializer(many=True)},
    )
    def get(self, request):
        """Get organization affiliations."""
        organization_affiliations = OrganizationAffiliation.objects.all()
        serializer = OrganizationAffiliationSerializer(
            organization_affiliations, many=True
        )
        return Response(serializer.data)

    @extend_schema(
        request=OrganizationAffiliationSerializer,
        responses={201: OrganizationAffiliationSerializer},
    )
    def post(self, request):
        """Create organization affiliation."""
        serializer = OrganizationAffiliationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrganizationAffiliationDetailview(APIView):
    """organization affiliation detail view."""

    def get_object(self, pk):
        """Get organization affiliation object."""
        try:
            return OrganizationAffiliation.objects.get(pk=pk)
        except OrganizationAffiliation.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: OrganizationAffiliationSerializer})
    def get(self, request, pk=None):
        """Get an organization affiliation by PK."""
        organization_affiliation = self.get_object(pk)
        serializer = OrganizationAffiliationSerializer(organization_affiliation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: OrganizationAffiliationSerializer})
    def patch(self, request, pk=None):
        """Update an organization affiliation object."""
        queryset = self.get_object(pk)
        serializer = OrganizationAffiliationSerializer(
            queryset, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """Delete an organization affiliation object."""
        queryset = self.get_object(pk)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
