"""Flag views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Flag
from .serializers import FlagSerializer


class FlagListView(APIView):
    """Flag list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: FlagSerializer(many=True)})
    def get(self, request):
        """Get all flags."""
        flags = Flag.objects.all()
        serializer = FlagSerializer(flags, many=True)
        return Response(serializer.data)

    @extend_schema(request=FlagSerializer, responses={201: FlagSerializer})
    def post(self, request):
        """Create a flag."""
        serializer = FlagSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FlagDetailView(APIView):
    """Flag detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get flag object."""
        try:
            return Flag.objects.get(pk=pk)
        except Flag.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: FlagSerializer})
    def get(self, request, pk):
        """Get a flag."""
        flag = self.get_object(pk)
        serializer = FlagSerializer(flag)
        return Response(serializer.data)

    @extend_schema(request=FlagSerializer, responses={200: FlagSerializer})
    def put(self, request, pk):
        """Update a flag."""
        flag = self.get_object(pk)
        serializer = FlagSerializer(flag, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a flag."""
        flag = self.get_object(pk)
        flag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
