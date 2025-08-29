"""Personal Relationships views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PersonalRelationship
from .serializers import PersonalRelationshipSerializer


class PersonalRelationshipListView(APIView):
    """Personal Relationship list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: PersonalRelationshipSerializer(many=True)})
    def get(self, request):
        """Get a list of personal relationships."""
        personal_relationships = PersonalRelationship.objects.all()
        serializer = PersonalRelationshipSerializer(personal_relationships, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=PersonalRelationshipSerializer,
        responses={201: PersonalRelationshipSerializer},
    )
    def post(self, request):
        """Create a personal relationship."""
        serializer = PersonalRelationshipSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PersonalRelationshipDetailView(APIView):
    """Personal Relationship detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a personal relationship object."""
        try:
            return PersonalRelationship.objects.get(pk=pk)
        except PersonalRelationship.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: PersonalRelationshipSerializer})
    def get(self, request, pk):
        """Get a personal relationship."""
        personal_relationship = self.get_object(pk)
        serializer = PersonalRelationshipSerializer(personal_relationship)
        return Response(serializer.data)

    @extend_schema(
        request=PersonalRelationshipSerializer,
        responses={200: PersonalRelationshipSerializer},
    )
    def put(self, request, pk):
        """Update a personal relationship."""
        personal_relationship = self.get_object(pk)
        serializer = PersonalRelationshipSerializer(
            personal_relationship, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a personal relationship."""
        personal_relationship = self.get_object(pk)
        personal_relationship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
