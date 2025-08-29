"""immunization evaluation views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from dfhir.immunizationevaluations.models import ImmunizationEvaluation
from dfhir.immunizationevaluations.serializers import ImmunizationEvaluationSerializer


class ImmunizationEvaluationListView(APIView):
    """immunization evaluation list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ImmunizationEvaluationSerializer(many=True)})
    def get(self, request):
        """Get immunization evaluation objects."""
        queryset = ImmunizationEvaluation.objects.all()
        serializer = ImmunizationEvaluationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ImmunizationEvaluationSerializer,
        responses={201: ImmunizationEvaluationSerializer},
    )
    def post(self, request):
        """Create immunization evaluation object."""
        serializer = ImmunizationEvaluationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ImmunizationEvaluationDetailView(APIView):
    """immunization evaluation detail view."""

    def get_object(self, pk):
        """Get immunization evaluation object."""
        try:
            return ImmunizationEvaluation.objects.get(pk=pk)
        except ImmunizationEvaluation.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ImmunizationEvaluationSerializer})
    def get(self, request, pk):
        """Get immunization evaluation object."""
        immunization_evaluation = self.get_object(pk)
        serializer = ImmunizationEvaluationSerializer(immunization_evaluation)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={200: ImmunizationEvaluationSerializer})
    def patch(self, request, pk):
        """Update immunization evaluation object."""
        immunization_evaluation = self.get_object(pk)
        serializer = ImmunizationEvaluationSerializer(
            immunization_evaluation, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: ImmunizationEvaluationSerializer})
    def delete(self, request, pk):
        """Delete immunization evaluation object."""
        immunization_evaluation = self.get_object(pk)
        immunization_evaluation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
