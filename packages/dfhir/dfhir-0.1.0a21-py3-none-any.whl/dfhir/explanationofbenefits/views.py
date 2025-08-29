"""Explanation of Benefits views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ExplanationOfBenefit
from .serializers import ExplanationOfBenefitSerializer


class ExplanationOfBenefitListView(APIView):
    """Explanation of Benefits list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: ExplanationOfBenefitSerializer(many=True)})
    def get(self, request):
        """Get a list of explanation of benefits."""
        explanation_of_benefits = ExplanationOfBenefit.objects.all()
        serializer = ExplanationOfBenefitSerializer(explanation_of_benefits, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ExplanationOfBenefitSerializer,
        responses={201: ExplanationOfBenefitSerializer},
    )
    def post(self, request):
        """Create a explanation of benefits."""
        serializer = ExplanationOfBenefitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExplanationOfBenefitDetailView(APIView):
    """Explanation of benefit detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get a care plan object."""
        try:
            return ExplanationOfBenefit.objects.get(pk=pk)
        except ExplanationOfBenefit.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ExplanationOfBenefitSerializer})
    def get(self, request, pk=None):
        """Get a care plan."""
        explanation_of_benefit = self.get_object(pk)
        serializer = ExplanationOfBenefitSerializer(explanation_of_benefit)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ExplanationOfBenefitSerializer,
        responses={200: ExplanationOfBenefitSerializer},
    )
    def patch(self, request, pk=None):
        """Update a care plan."""
        explanation_of_benefit = self.get_object(pk)
        serializer = ExplanationOfBenefitSerializer(
            explanation_of_benefit, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete a care plan."""
        explanation_of_benefit = self.get_object(pk)
        explanation_of_benefit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
