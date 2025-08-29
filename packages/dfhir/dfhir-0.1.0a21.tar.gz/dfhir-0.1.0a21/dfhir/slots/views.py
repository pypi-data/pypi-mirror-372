"""Slots views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import SlotsFilter
from .models import Slot
from .serializers import SlotSerializer


class SlotListView(APIView):
    """Slot list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: SlotSerializer(many=True)})
    def get(self, request):
        """Get slots."""
        slots = Slot.objects.all()
        filterd_slots = SlotsFilter(request.GET, queryset=slots)
        serializer = SlotSerializer(filterd_slots.qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new slot."""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class SlotDetailView(APIView):
    """Slot detail view."""

    def get_object(self, pk):
        """Get slot object."""
        try:
            return Slot.objects.get(pk=pk)
        except Slot.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: SlotSerializer})
    def get(self, request, pk=None):
        """Get slot."""
        slot = self.get_object(pk)
        serializer = SlotSerializer(slot)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: SlotSerializer})
    def patch(self, request, pk=None):
        """Update slot."""
        slot = self.get_object(pk)
        serializer = SlotSerializer(slot, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
