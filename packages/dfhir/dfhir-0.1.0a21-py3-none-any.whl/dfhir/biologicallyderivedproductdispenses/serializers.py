"""biologically derived product dispenses serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    SimpleQuantitySerializer,
)
from dfhir.biologicallyderivedproductdispenses.models import (
    BiologicallyDerivedProductDispense,
    BiologicallyDerivedProductDispensePerformer,
    BiologicallyDerivedProductDispenseReference,
)
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer
from dfhir.practitioners.serializers import PractitionerReferenceSerializer
from dfhir.servicerequests.serializers import ServiceRequestReferenceSerializer


class BiologicallyDerivedProductDispenseReferenceSerializer(
    BaseReferenceModelSerializer
):
    """biologically derived product dispense reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = BiologicallyDerivedProductDispenseReference
        exclude = ["created_at", "updated_at"]


class BiologicallyDerivedProductDispensePerformerSerializer(
    WritableNestedModelSerializer
):
    """biologically derived product dispense performer serializer."""

    function = CodeableConceptSerializer(required=False)
    actor = PractitionerReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = BiologicallyDerivedProductDispensePerformer
        exclude = ["created_at", "updated_at"]


class BiologicallyDerivedProductDispenseSerializer(BaseWritableNestedModelSerializer):
    """biologically derived product dispense serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    based_on = ServiceRequestReferenceSerializer(required=False, many=True)
    part_of = BiologicallyDerivedProductDispenseReferenceSerializer(
        required=False, many=True
    )
    original_relationship = CodeableConceptSerializer(required=False)
    product = BiologicallyDerivedProductDispenseReferenceSerializer(required=False)
    patient = PatientReferenceSerializer(required=False)
    performer = BiologicallyDerivedProductDispensePerformerSerializer(
        required=False, many=True
    )
    location = LocationReferenceSerializer(required=False)
    quantity = SimpleQuantitySerializer(required=False)
    destination = LocationReferenceSerializer(required=False)
    note = AnnotationSerializer(required=False)

    class Meta:
        """meta options."""

        model = BiologicallyDerivedProductDispense
        exclude = ["created_at", "updated_at"]
