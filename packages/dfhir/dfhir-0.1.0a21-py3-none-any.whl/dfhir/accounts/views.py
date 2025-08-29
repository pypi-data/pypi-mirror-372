"""Accounts views."""

from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account
from .serializers import AccountSerializer


class AccountListView(APIView):
    """Account list view."""

    permission_classes = [AllowAny]

    @extend_schema(responses={200: AccountSerializer(many=True)})
    def get(self, request):
        """Get a list of accounts."""
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data)

    @extend_schema(request=AccountSerializer, responses={201: AccountSerializer})
    def post(self, request):
        """Create an account."""
        serializer = AccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AccountDetailView(APIView):
    """Account detail view."""

    permission_classes = [AllowAny]

    def get_object(self, pk):
        """Get an account object."""
        try:
            return Account.objects.get(pk=pk)
        except Account.DoesNotExist as err:
            raise Http404 from err

    @extend_schema(responses={200: AccountSerializer})
    def get(self, request, pk=None):
        """Get an account."""
        account = self.get_object(pk)
        serializer = AccountSerializer(account)
        return Response(serializer.data)

    @extend_schema(request=AccountSerializer, responses={200: AccountSerializer})
    def patch(self, request, pk=None):
        """Update an account."""
        account = self.get_object(pk)
        serializer = AccountSerializer(account, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @extend_schema(responses={204: None})
    def delete(self, request, pk=None):
        """Delete an account."""
        account = self.get_object(pk)
        account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
