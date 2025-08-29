"""medication statements views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.medicationstatements.models import MedicationStatement
from dfhir.medicationstatements.serializers import MedicationStatementSerializer


class MedicationStatementListView(APIView):
    """medication statement list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: MedicationStatementSerializer(many=True)})
    def get(self, request):
        """Get medication statement list."""
        medication_statements = MedicationStatement.objects.all()
        serializer = MedicationStatementSerializer(medication_statements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=MedicationStatementSerializer,
        responses={201: MedicationStatementSerializer},
    )
    def post(self, request):
        """Create medication statement."""
        serializer = MedicationStatementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MedicationStatementDetailedView(APIView):
    """medication statement detailed view."""

    def get_object(self, pk):
        """Get medication statement object."""
        try:
            return MedicationStatement.objects.get(pk=pk)

        except MedicationStatement.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200, MedicationStatementSerializer})
    def get(self, request, pk):
        """Get a medication statement."""
        medication_statement = self.get_object(pk)
        serializer = MedicationStatementSerializer(medication_statement)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=MedicationStatementSerializer,
        responses={200: MedicationStatementSerializer},
    )
    def patch(self, request, pk):
        """Update medication statement."""
        medication_statement = self.get_object(pk)
        serializer = MedicationStatementSerializer(
            medication_statement, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk):
        """Delete medication statement."""
        medication_statement = self.get_object(pk)
        medication_statement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
