"""Procedure views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Procedure
from .serializers import ProcedureSerializer


class ProcedureListView(APIView):
    """Procedure List Views."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ProcedureSerializer(many=True)})
    def get(self, request):
        """Get all procedures."""
        procedures = Procedure.objects.all()
        serializer = ProcedureSerializer(procedures, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ProcedureSerializer, responses={201: ProcedureSerializer})
    def post(self, request):
        """Create a procedure."""
        serializer = ProcedureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProcedureDetailView(APIView):
    """Procedure Detail View."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a procedure object."""
        try:
            return Procedure.objects.get(pk=pk)
        except Procedure.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ProcedureSerializer})
    def get(self, request, pk):
        """Get a procedure."""
        procedure = self.get_object(pk)
        serializer = ProcedureSerializer(procedure)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ProcedureSerializer, responses={200: ProcedureSerializer})
    def patch(self, request, pk):
        """Update a procedure."""
        procedure = self.get_object(pk)
        serializer = ProcedureSerializer(procedure, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete a procedure."""
        procedure = self.get_object(pk)
        procedure.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
