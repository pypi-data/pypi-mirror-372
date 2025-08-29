"""body structure views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.bodystructures.models import BodyStructure
from dfhir.bodystructures.serializers import BodyStructureSerializer


class BodyStructureListView(APIView):
    """body structure view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: BodyStructureSerializer(many=True)})
    def get(self, request):
        """Get body structures."""
        body_structures = BodyStructure.objects.all()
        serializer = BodyStructureSerializer(body_structures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=BodyStructureSerializer, responses={201: BodyStructureSerializer}
    )
    def post(self, request):
        """Create body structure."""
        serializer = BodyStructureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BodyStructureDetailView(APIView):
    """body structure detail view."""

    def get_object(self, pk):
        """Get object."""
        try:
            return BodyStructure.objects.get(pk=pk)
        except BodyStructure.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: BodyStructureSerializer})
    def get(self, request, pk):
        """Get body structure."""
        body_structure = self.get_object(pk)
        serializer = BodyStructureSerializer(body_structure)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=BodyStructureSerializer, responses={200: BodyStructureSerializer}
    )
    def patch(self, request, pk):
        """Update body structure."""
        body_structure = self.get_object(pk)
        serializer = BodyStructureSerializer(
            body_structure, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete body structure."""
        body_structure = self.get_object(pk)
        body_structure.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
