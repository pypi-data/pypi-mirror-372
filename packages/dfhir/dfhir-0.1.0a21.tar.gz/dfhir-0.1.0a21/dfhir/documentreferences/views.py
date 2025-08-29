"""document reference views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.documentreferences.models import DocumentReference
from dfhir.documentreferences.serializers import DocumentReferenceSerializer


class DocumentReferenceListView(APIView):
    """DocumentReference list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: DocumentReferenceSerializer(many=True)})
    def get(self, request):
        """Get document references."""
        document_references = DocumentReference.objects.all()
        serializer = DocumentReferenceSerializer(document_references, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=DocumentReferenceSerializer,
        responses={201: DocumentReferenceSerializer},
    )
    def post(self, request):
        """Create a document reference."""
        serializer = DocumentReferenceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DocumentReferenceDetailView(APIView):
    """DocumentReference detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get document reference object."""
        try:
            return DocumentReference.objects.get(pk=pk)
        except DocumentReference.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: DocumentReferenceSerializer})
    def get(self, request, pk):
        """Get a document reference."""
        document_reference = self.get_object(pk)
        serializer = DocumentReferenceSerializer(document_reference)
        return Response(serializer.data)

    @extend_schema(
        request=DocumentReferenceSerializer,
        responses={200: DocumentReferenceSerializer},
    )
    def patch(self, request, pk):
        """Update a document reference."""
        document_reference = self.get_object(pk)
        serializer = DocumentReferenceSerializer(
            document_reference, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a document reference."""
        document_reference = self.get_object(pk)
        document_reference.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
