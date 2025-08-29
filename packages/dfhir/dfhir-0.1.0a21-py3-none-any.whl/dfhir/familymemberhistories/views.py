"""Family member history views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FamilyMemberHistory
from .serializers import FamilyMemberHistorySerializer


class FamilyMemberHistoryListView(APIView):
    """Family member history list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: FamilyMemberHistorySerializer(many=True)})
    def get(self, request):
        """Get a list of family member histories."""
        family_member_histories = FamilyMemberHistory.objects.all()
        serializer = FamilyMemberHistorySerializer(family_member_histories, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=FamilyMemberHistorySerializer,
        responses={201: FamilyMemberHistorySerializer},
    )
    def post(self, request):
        """Create a family member history."""
        serializer = FamilyMemberHistorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FamilyMemberHistoryDetailView(APIView):
    """Family member history detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a family member history object."""
        try:
            return FamilyMemberHistory.objects.get(pk=pk)
        except FamilyMemberHistory.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: FamilyMemberHistorySerializer})
    def get(self, request, pk):
        """Get a family member history."""
        family_member_history = self.get_object(pk)
        serializer = FamilyMemberHistorySerializer(family_member_history)
        return Response(serializer.data)

    @extend_schema(
        request=FamilyMemberHistorySerializer,
        responses={200: FamilyMemberHistorySerializer},
    )
    def patch(self, request, pk):
        """Update a family member history."""
        family_member_history = self.get_object(pk)
        serializer = FamilyMemberHistorySerializer(
            family_member_history, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a family member history."""
        family_member_history = self.get_object(pk)
        family_member_history.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
