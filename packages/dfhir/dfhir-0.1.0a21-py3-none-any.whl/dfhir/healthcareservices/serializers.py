"""Healthcare services serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.models import ServiceType
from dfhir.base.serializers import (
    AttachmentSerializer,
    AvailabilitySerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    ExtendedContactDetailSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    QuantitySerializer,
    RangeSerializer,
    ReferenceSerializer,
)
from dfhir.endpoints.serializers import EndpointSerializer
from dfhir.locations.serializers import LocationReferenceSerializer

from .models import (
    ClinicalSpecialty,
    HealthcareService,
    HealthCareServiceCodeableReference,
    HealthcareServiceEligibility,
    HealthCareServiceEligibilityValue,
    HealthCareServiceReference,
    ServiceCategory,
)


class HealthCareServiceReferenceSerializer(BaseReferenceModelSerializer):
    """HealthCareService reference serializer."""

    class Meta:
        """Meta class."""

        model = HealthCareServiceReference
        exclude = ["created_at", "updated_at"]


class HealthCareServiceCodeableReferenceSerializer(WritableNestedModelSerializer):
    """CodeableReference serializer."""

    reference = HealthCareServiceReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = HealthCareServiceCodeableReference
        exclude = ["created_at", "updated_at"]


class HealthcareServiceEligibilityValueSerializer(serializers.ModelSerializer):
    """Healthcare Service Eligibility Value serializer."""

    value_codeable_concept = CodeableConceptSerializer(required=False)
    value_quantity = QuantitySerializer(required=False)
    value_range = RangeSerializer(required=False)
    value_reference = ReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = HealthCareServiceEligibilityValue
        exclude = ["created_at", "updated_at"]


class HealthcareServiceEligibilitySerializer(WritableNestedModelSerializer):
    """Healthcare Service Eligibility serializer."""

    code = CodeableConceptSerializer(required=False)
    value = HealthcareServiceEligibilityValueSerializer(required=False)

    class Meta:
        """Meta class."""

        model = HealthcareServiceEligibility
        exclude = ["created_at", "updated_at"]


class HealthcareServiceSerializer(BaseWritableNestedModelSerializer):
    """Healthcare Service serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    offered_in = HealthCareServiceReferenceSerializer(many=True, required=False)
    location = LocationReferenceSerializer(many=True, required=False)
    contact = ExtendedContactDetailSerializer(many=True, required=False)
    provided_by = OrganizationReferenceSerializer(required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    specialty = CodeableConceptSerializer(many=True, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    coverage_area = LocationReferenceSerializer(many=True, required=False)
    service_provision_code = CodeableConceptSerializer(many=True, required=False)
    eligibility = HealthcareServiceEligibilitySerializer(many=True, required=False)
    characteristic = CodeableConceptSerializer(many=True, required=False)
    communication = CodeableConceptSerializer(many=True, required=False)
    availability = AvailabilitySerializer(many=False, required=False)
    program = CodeableConceptSerializer(many=True, required=False)
    photo = AttachmentSerializer(required=False)
    referral_method = CodeableConceptSerializer(many=True, required=False)
    endpoint = EndpointSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = HealthcareService

        exclude = ["created_at", "updated_at"]


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Service Category serializer."""

    class Meta:
        """Meta class."""

        model = ServiceCategory
        exclude = ["created_at", "updated_at"]


class ClinicalSpecialtySerializer(serializers.ModelSerializer):
    """Clinical Specialty Valueset serializer."""

    class Meta:
        """Meta class."""

        model = ClinicalSpecialty
        exclude = ["created_at", "updated_at"]


class ServiceTypeSerializer(serializers.ModelSerializer):
    """Service Type serializer."""

    class Meta:
        """Meta class."""

        model = ServiceType
        exclude = ["created_at", "updated_at"]
