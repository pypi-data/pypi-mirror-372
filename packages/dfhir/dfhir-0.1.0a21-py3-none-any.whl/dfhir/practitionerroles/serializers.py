"""practitioner role serializers."""

from rest_framework import serializers

from dfhir.base.serializers import (
    AvailabilitySerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    ExtendedContactDetailSerializer,
    IdentifierSerializer,
    PeriodSerializer,
)
from dfhir.endpoints.serializers import EndpointReferenceSerializer
from dfhir.healthcareservices.serializers import HealthCareServiceReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.organizations.serializers import OrganizationReferenceSerializer
from dfhir.practitionerroles.models import (
    PractitionerRole,
    PractitionerRoleCode,
    PractitionerRoleReference,
)
from dfhir.practitioners.serializers import (
    PractitionerReferenceSerializer,
)


class PractitionerRoleCodeSerializer(serializers.ModelSerializer):
    """Practitioner Role Code serializer."""

    class Meta:
        """Meta class."""

        model = PractitionerRoleCode
        exclude = ["created_at", "updated_at"]


# Practitioner role
class PractitionerRoleSerializer(BaseWritableNestedModelSerializer):
    """Practitioner Role serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    period = PeriodSerializer(many=False, required=False)
    practitioner = PractitionerReferenceSerializer(many=False, required=False)
    organization = OrganizationReferenceSerializer(many=False, required=False)
    network = OrganizationReferenceSerializer(many=True, required=False)
    code = CodeableConceptSerializer(many=True, required=False)
    specialty = CodeableConceptSerializer(many=True, required=False)
    location = LocationReferenceSerializer(many=True, required=False)
    healthcare_service = HealthCareServiceReferenceSerializer(many=True, required=False)
    characteristic = CodeableConceptSerializer(many=True, required=False)
    availability = AvailabilitySerializer(many=False, required=False)
    communication = CodeableConceptSerializer(many=True, required=False)
    contact = ExtendedContactDetailSerializer(many=True, required=False)
    endpoint = EndpointReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = PractitionerRole
        exclude = ["created_at", "updated_at"]


class PractitionerRoleWithPractitionerIdSerializer(PractitionerRoleSerializer):
    """Practitioner Role with Practitioner ID serializer."""

    class Meta:
        """Meta class."""

        model = PractitionerRole
        exclude = ["created_at", "updated_at"]


class PractitionerRoleReferenceSerializer(BaseReferenceModelSerializer):
    """Practitioner Role reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = PractitionerRoleReference
        exclude = ["created_at", "updated_at"]
