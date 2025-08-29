"""relatedpersons views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RelatedPerson
from .serializers import RelatedPersonSerializer


class RelatedPersonListView(APIView):
    """Related person list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: RelatedPersonSerializer(many=True)})
    def get(self, request):
        """Get related person list."""
        related_persons = RelatedPerson.objects.all()
        serializer = RelatedPersonSerializer(related_persons, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=RelatedPersonSerializer, responses={201: RelatedPersonSerializer}
    )
    def post(self, request):
        """Create a related person."""
        serializer = RelatedPersonSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RelatedPersonDetailView(APIView):
    """Related person detail view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: RelatedPersonSerializer})
    def get(self, request, related_person_id):
        """Get related person detail."""
        try:
            related_person = RelatedPerson.objects.get(id=related_person_id)
        except RelatedPerson.DoesNotExist as err:
            raise Http404 from err

        serializer = RelatedPersonSerializer(related_person)
        return Response(serializer.data)

    @extend_schema(
        request=RelatedPersonSerializer, responses={200: RelatedPersonSerializer}
    )
    def put(self, request, related_person_id):
        """Update related person."""
        try:
            related_person = RelatedPerson.objects.get(id=related_person_id)
        except RelatedPerson.DoesNotExist as err:
            raise Http404 from err

        serializer = RelatedPersonSerializer(related_person, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, related_person_id):
        """Delete related person."""
        try:
            related_person = RelatedPerson.objects.get(id=related_person_id)
        except RelatedPerson.DoesNotExist as err:
            raise Http404 from err

        related_person.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
