"""Vision prescription serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    SimpleQuantitySerializer,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)

from .models import (
    VisionPrescription,
    VisionPrescriptionBasedOnReference,
    VisionPrescriptionLensSpecification,
    VisionPrescriptionLensSpecificationPrism,
)


class VisionPrescriptionBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """Vision Prescription Based On Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = VisionPrescriptionBasedOnReference
        exclude = ["created_at", "updated_at"]


class VisionPrescriptionLensSpecificationPrismSerializer(WritableNestedModelSerializer):
    """Vision Prescription Lens Specification Prism Serializer."""

    class Meta:
        """Meta class."""

        model = VisionPrescriptionLensSpecificationPrism
        exclude = ["created_at", "updated_at"]


class VisionPrescriptionLensSpecificationSerializer(WritableNestedModelSerializer):
    """Vision Prescription Lens Specification Serializer."""

    product = CodeableConceptSerializer(many=False, required=False)
    prism = VisionPrescriptionLensSpecificationPrismSerializer(
        many=True, required=False
    )
    duration = SimpleQuantitySerializer(many=False, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = VisionPrescriptionLensSpecification
        exclude = ["created_at", "updated_at"]


class VisionPrescriptionSerializer(BaseWritableNestedModelSerializer):
    """Vision Prescription Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = VisionPrescriptionBasedOnReferenceSerializer(many=True, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    prescriber = PractitionerPractitionerRoleReferenceSerializer(
        many=False, required=False
    )
    lens_specification = VisionPrescriptionLensSpecificationSerializer(
        many=True, required=False
    )

    class Meta:
        """Meta class."""

        model = VisionPrescription
        exclude = ["created_at", "updated_at"]
