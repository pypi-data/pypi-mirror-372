"""Enrollment responses serializers."""

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
)
from dfhir.enrollmentrequests.serializers import EnrollmentRequestReferenceSerializer

from .models import (
    EnrollmentResponse,
    EnrollmentResponseRequestProviderReference,
)


class EnrollmentResponseRequestProviderReferenceSerializer(
    BaseReferenceModelSerializer
):
    """EnrollmentResponse Request Provider Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = EnrollmentResponseRequestProviderReference
        exclude = ["created_at", "updated_at"]


class EnrollmentResponseSerializer(BaseWritableNestedModelSerializer):
    """EnrollmentResponse Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    request = EnrollmentRequestReferenceSerializer(required=False)
    organization = OrganizationReferenceSerializer(required=False)
    request_provider = EnrollmentResponseRequestProviderReferenceSerializer(
        required=False
    )

    class Meta:
        """Meta class."""

        model = EnrollmentResponse
        exclude = ["created_at", "updated_at"]
