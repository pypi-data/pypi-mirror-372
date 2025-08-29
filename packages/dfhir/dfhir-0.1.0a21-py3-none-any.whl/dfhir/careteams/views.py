"""CareTeams views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CareTeam
from .serializers import CareTeamSerializer


class CareTeamListView(APIView):
    """CareTeam list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: CareTeamSerializer(many=True)})
    def get(self, request):
        """Get a list of care teams."""
        care_teams = CareTeam.objects.all()
        serializer = CareTeamSerializer(care_teams, many=True)
        return Response(serializer.data)

    @extend_schema(request=CareTeamSerializer, responses={201: CareTeamSerializer})
    def post(self, request):
        """Create a care team."""
        serializer = CareTeamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CareTeamDetailView(APIView):
    """CareTeam detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a care team object."""
        try:
            return CareTeam.objects.get(pk=pk)
        except CareTeam.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: CareTeamSerializer})
    def get(self, request, pk):
        """Get a care team."""
        care_team = self.get_object(pk)
        serializer = CareTeamSerializer(care_team)
        return Response(serializer.data)

    @extend_schema(request=CareTeamSerializer, responses={200: CareTeamSerializer})
    def put(self, request, pk):
        """Update a care team."""
        care_team = self.get_object(pk)
        serializer = CareTeamSerializer(care_team, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a care team."""
        care_team = self.get_object(pk)
        care_team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
