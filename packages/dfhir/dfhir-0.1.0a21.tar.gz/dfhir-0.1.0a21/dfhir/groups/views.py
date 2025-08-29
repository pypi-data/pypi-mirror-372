"""Groups views."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Group
from .serializers import GroupSerializer


class GroupListView(APIView):
    """Group list view."""

    serializer = GroupSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses={200, GroupSerializer(many=True)})
    def get(self, request):
        """Get all groups."""
        groups = Group.objects.all()
        serializer = self.serializer(groups, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=GroupSerializer,
        responses={201, GroupSerializer},
    )
    def post(self, request):
        """Create a new group."""
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupDetailView(APIView):
    """Group detail view."""

    serializer = GroupSerializer

    def get_object(self, pk=None):
        """Get group object."""
        try:
            return Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(responses={200, GroupSerializer})
    def get(self, request, pk):
        """Get group."""
        group = self.get_object(pk)
        serializer = self.serializer(group)
        return Response(serializer.data)

    @extend_schema(
        request=GroupSerializer,
        responses={200, GroupSerializer},
    )
    def put(self, request, pk):
        """Update group."""
        group = self.get_object(pk)
        serializer = self.serializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204})
    def delete(self, request, pk):
        """Delete group."""
        group = self.get_object(pk)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
