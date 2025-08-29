"""Organization views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.organizations.models import Organization
from dfhir.organizations.serializers import OrganizationSerializer

# print(CreateOrganizationSchema.schema())

DATA = {
    "id": 1,
    "name": "City General Hospital",
    "alias": "CGH",
    "website": "https://www.citygeneralhospital.org",
    "email": "info@citygeneralhospital.org",
    "admin_id": 101,
    "status": "active",
    "active": True,
    "type": "hospital_department",
    # "part_of_id": None,
    "description": "A leading hospital providing comprehensive healthcare services to the city.",
    "location": [
        {
            "id": 10,
            "name": "Main Building",
            "status": "active",
            "operational_status": "occupied",
            "alias": "MB",
            "description": "The main building houses the emergency department and outpatient clinics.",
            "mode": "instance",
            "address": "123 Main Street, Springfield",
            "form": "building",
            "position": '{"latitude": 37.7749, "longitude": -122.4194}',
            # "part_of_id": None,
            "hours_of_operation": '{"Monday-Friday": "8 AM - 8 PM", "Saturday": "9 AM - 5 PM"}',
        },
        {
            "id": 11,
            "name": "Emergency Wing",
            "status": "active",
            "operational_status": "occupied",
            "alias": "EW",
            "description": "Dedicated wing for emergency cases.",
            "mode": "instance",
            "address": "123 Main Street, Springfield",
            "form": "wing",
            "position": '{"latitude": 37.7750, "longitude": -122.4195}',
            "part_of_id": 10,
            "hours_of_operation": '{"24/7": true}',
        },
    ],
    "contact": [
        {
            "id": 1,
            "purpose": "General Inquiries",
            "name": "Main Reception",
            "address": "123 Main Street, Springfield",
            "period": "Monday-Friday: 8 AM - 8 PM",
        },
        {
            "id": 2,
            "purpose": "Emergency Contact",
            "name": "Emergency Services",
            "address": "123 Main Street, Springfield",
            "period": "24/7",
        },
    ],
}


# class OrganizationListView(APIView):
#     """Organization list view."""
#
#     permission_classes = [AllowAny]
#
#     @extend_schema(responses={200: OrganizationSerializer(many=True)})
#     def get(self, request, pk=None):
#         """Get organizations."""
#         queryset = Organization.objects.all()
#         serializer = OrganizationSerializer(queryset, many=True)
#         return Response(serializer.data)
#
#     @extend_schema(
#         request=OrganizationSerializer, responses={200: OrganizationSerializer}
#     )
#     def post(self, request):
#         """Create organization."""
#         request_data = request.data
#         serializer = OrganizationSerializer(data=request_data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


class OrganizationListView(APIView):
    """Organization list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: OrganizationSerializer(many=True)})
    def get(self, request, pk=None):
        """Get organizations."""
        queryset = Organization.objects.all()
        serializer = OrganizationSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=OrganizationSerializer, responses={200: OrganizationSerializer}
    )
    def post(self, request):
        """Create organization."""
        request_data = request.data
        serializer = OrganizationSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class OrganizationDetailView(APIView):
    """Organization detail view."""

    def get_object(self, pk):
        """Get organization object."""
        try:
            return Organization.objects.get(pk=pk)
        except Organization.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: OrganizationSerializer})
    def get(self, request, pk=None):
        """Get organization."""
        queryset = self.get_object(pk)
        serializer = OrganizationSerializer(queryset)
        return Response(serializer.data)

    @extend_schema(responses={200: OrganizationSerializer})
    def patch(self, request, pk=None):
        """Update organization."""
        queryset = self.get_object(pk)
        serializer = OrganizationSerializer(queryset, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk=None):
        """Delete organization."""
        organization = self.get_object(pk)
        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
