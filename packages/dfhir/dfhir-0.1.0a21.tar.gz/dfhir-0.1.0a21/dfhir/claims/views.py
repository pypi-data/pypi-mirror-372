"""Claims views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Claim
from .serializers import ClaimSerializer


class ClaimListView(APIView):
    """Claim list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ClaimSerializer(many=True)})
    def get(self, request):
        """Get a list of claims."""
        claims = Claim.objects.all()
        serializer = ClaimSerializer(claims, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ClaimSerializer, responses={201: ClaimSerializer})
    def post(self, request):
        """Create a claim."""
        serializer = ClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ClaimDetailView(APIView):
    """Claim detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a claim object."""
        try:
            return Claim.objects.get(pk=pk)
        except Claim.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ClaimSerializer})
    def get(self, request, pk=None):
        """Get a claim."""
        claim = self.get_object(pk)
        serializer = ClaimSerializer(claim)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ClaimSerializer, responses={200: ClaimSerializer})
    def patch(self, request, pk=None):
        """Update a claim."""
        claim = self.get_object(pk)
        serializer = ClaimSerializer(claim, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a claim."""
        claim = self.get_object(pk)
        claim.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
