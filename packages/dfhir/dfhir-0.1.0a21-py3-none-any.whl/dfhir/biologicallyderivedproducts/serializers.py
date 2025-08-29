"""Biolocically Derived Products serializers."""

from dfhir.base.serializers import (
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodingSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    QuantitySerializer,
    RangeSerializer,
    RatioSerializer,
)
from dfhir.patients.serializers import PatientOrganizationReferenceSerializer
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)
from dfhir.procedures.serializers import ProcedureSerializer
from dfhir.servicerequests.serializers import ServiceRequestReferenceSerializer

from .models import (
    BiologicallyDerivedProduct,
    BiologicallyDerivedProductCollection,
    BiologicallyDerivedProductProperty,
    BiologicallyDerivedProductReference,
)


class BiologicallyDerivedProductReferenceSerializer(BaseReferenceModelSerializer):
    """Biologically Derived Product Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = BiologicallyDerivedProductReference
        exclude = ["created_at", "updated_at"]


class BiologicallyDerivedProductCollectionSerializer(BaseWritableNestedModelSerializer):
    """Biologically Derived Product Collection serializer."""

    collector = PractitionerPractitionerRoleReferenceSerializer(required=False)
    source = PatientOrganizationReferenceSerializer(required=False)
    collected_period = PeriodSerializer(required=False)
    procedure = ProcedureSerializer(required=False)

    class Meta:
        """Meta class."""

        model = BiologicallyDerivedProductCollection
        exclude = ["created_at", "updated_at"]


class BiologicallyDerivedProductPropertySerializer(BaseWritableNestedModelSerializer):
    """Biologically Derived Product Property serializer."""

    type = CodeableConceptSerializer(required=False)
    value_codeable_concept = CodeableConceptSerializer(required=False)
    value_period = PeriodSerializer(required=False)
    value_quantity = QuantitySerializer(required=False)
    value_range = RangeSerializer(required=False)
    value_ratio = RatioSerializer(required=False)
    value_attachment = AttachmentSerializer(required=False)

    class Meta:
        """Meta class."""

        model = BiologicallyDerivedProductProperty
        exclude = ["created_at", "updated_at"]


class BiologicallyDerivedProductSerializer(BaseWritableNestedModelSerializer):
    """Biologically Derived Product serializer."""

    product_category = CodeableConceptSerializer(required=False, many=True)
    product_code = CodeableConceptSerializer(required=False)
    parent = BiologicallyDerivedProductReferenceSerializer(required=False, many=True)
    request = ServiceRequestReferenceSerializer(required=False, many=True)
    identifier = IdentifierSerializer(many=True, required=False)
    biological_source_event = IdentifierSerializer(required=False)
    processing_facility = OrganizationReferenceSerializer(required=False, many=True)
    product_status = CodingSerializer(required=False)
    collection = BiologicallyDerivedProductCollectionSerializer(required=False)
    storage_temp_requirements = RangeSerializer(required=False)
    property = BiologicallyDerivedProductPropertySerializer(required=False, many=True)

    class Meta:
        """Meta class."""

        model = BiologicallyDerivedProduct
        exclude = ["created_at", "updated_at"]
