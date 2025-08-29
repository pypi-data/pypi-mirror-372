"""Enrollment request serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
)
from dfhir.coverages.serializers import CoverageReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer

from .models import (
    EnrollmentRequest,
    EnrollmentRequestProviderReference,
    EnrollmentRequestsReference,
)


class EnrollmentRequestProviderReferenceSerializer(BaseReferenceModelSerializer):
    """Enrollment Request Provider Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = EnrollmentRequestProviderReference
        exclude = ["created_at", "updated_at"]


class EnrollmentRequestSerializer(WritableNestedModelSerializer):
    """Enrollment Request serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    insurer = OrganizationReferenceSerializer(many=False, required=False)
    provider = EnrollmentRequestProviderReferenceSerializer(many=False, required=False)
    candidate = PatientReferenceSerializer(many=False, required=False)
    coverage = CoverageReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = EnrollmentRequest
        exclude = ["created_at", "updated_at"]


class EnrollmentRequestReferenceSerializer(BaseReferenceModelSerializer):
    """Enrollment Requests Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = EnrollmentRequestsReference
        exclude = ["created_at", "updated_at"]
