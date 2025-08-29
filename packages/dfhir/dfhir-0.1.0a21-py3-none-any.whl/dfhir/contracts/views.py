"""Contract views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Contract
from .serializers import ContractSerializer


class ContractListView(APIView):
    """Contract list create view."""

    permission_classes = [AllowAny]

    @extend_schema(request=ContractSerializer, responses={201: ContractSerializer})
    def post(self, request):
        """Create a contract."""
        serializer = ContractSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(responses={200: ContractSerializer(many=True)})
    def get(self, request):
        """Get all contracts."""
        contracts = Contract.objects.all()
        serializer = ContractSerializer(contracts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContractDetailView(APIView):
    """Contract detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get contract object."""
        try:
            return Contract.objects.get(id=pk)
        except Contract.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: ContractSerializer})
    def get(self, request, pk=None):
        """Get contract detail."""
        contract = self.get_object(pk)
        serializer = ContractSerializer(contract)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=ContractSerializer, responses={200: ContractSerializer})
    def patch(self, request, pk=None):
        """Update contract."""
        contract = self.get_object(pk)
        serializer = ContractSerializer(contract, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete contract."""
        contract = self.get_object(pk)
        contract.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
