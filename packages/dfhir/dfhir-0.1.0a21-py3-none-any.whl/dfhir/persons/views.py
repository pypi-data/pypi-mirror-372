"""Persons views."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Person
from .serializers import PersonSerializer


class PersonListView(APIView):
    """Healthcare Service list view."""

    serializer = PersonSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses={200, PersonSerializer(many=True)})
    def get(self, request):
        """Get all healthcare services."""
        persons = Person.objects.all()
        serializer = self.serializer(persons, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=PersonSerializer,
        responses={201, PersonSerializer},
    )
    def post(self, request):
        """Create a new healthcare service."""
        serializer = self.serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonDetailView(APIView):
    """Healthcare Service detail view."""

    serializer = PersonSerializer

    def get_object(self, pk=None):
        """Get healthcare service object."""
        try:
            return Person.objects.get(pk=pk)
        except Person.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(responses={200, PersonSerializer})
    def get(self, request, pk):
        """Get a healthcare service."""
        person = self.get_object(pk)
        serializer = self.serializer(person)
        return Response(serializer.data)

    @extend_schema(responses={200, PersonSerializer})
    def patch(self, request, pk):
        """Update a healthcare service."""
        person = self.get_object(pk)
        serializer = self.serializer(person, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Delete a healthcare service."""
        person = self.get_object(pk)
        person.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
