"""risk assessment views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.riskassessments.models import RiskAssessment
from dfhir.riskassessments.serializers import RiskAssessmentSerializer


class RiskManagementListView(APIView):
    """risk management list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: RiskAssessmentSerializer(many=True)})
    def get(self, request):
        """Get."""
        risk_assessments = RiskAssessment.objects.all()
        serializer = RiskAssessmentSerializer(risk_assessments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=RiskAssessmentSerializer, responses={201: RiskAssessmentSerializer}
    )
    def post(self, request):
        """Post."""
        serializer = RiskAssessmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RiskAssessmentDetialView(APIView):
    """risk assessment detail view."""

    def get_object(self, pk):
        """Get object."""
        try:
            return RiskAssessment.objects.get(pk=pk)
        except RiskAssessment.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: RiskAssessmentSerializer})
    def get(self, request, pk=None):
        """Get a risk assessment object by ID."""
        risk_assessment = self.get_object(pk)
        serializer = RiskAssessmentSerializer(risk_assessment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=RiskAssessmentSerializer, responses={200: RiskAssessmentSerializer}
    )
    def patch(self, request, pk=None):
        """Update a risk assessment object by ID."""
        risk_assessment = self.get_object(pk)
        serializer = RiskAssessmentSerializer(
            risk_assessment, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a risk assessment object by ID."""
        risk_assessment = self.get_object(pk)
        risk_assessment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
