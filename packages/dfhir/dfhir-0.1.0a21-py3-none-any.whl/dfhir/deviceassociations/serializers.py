"""Deviceassociations serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
)
from dfhir.bodystructures.serializers import BodyStructureReferenceSerializer
from dfhir.devices.serializers import DeviceReferenceSerializer

from .models import (
    DeviceAssociation,
    DeviceAssociationOperation,
    DeviceAssociationOperationOperatorReference,
    DeviceAssociationSubjectReference,
)


class DeviceAssociationSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """Device Association Subject Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = DeviceAssociationSubjectReference
        exclude = ["created_at", "updated_at"]


class DeviceAssociationOperationOperatorReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Device Association Operation Operator Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = DeviceAssociationOperationOperatorReference
        exclude = ["created_at", "updated_at"]


class DeviceAssociationOperationSerializer(WritableNestedModelSerializer):
    """Device Association Operation Serializer."""

    status = CodeableConceptSerializer(many=False, required=False)
    operator = DeviceAssociationOperationOperatorReferenceSerializer(
        many=True, required=False
    )
    period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceAssociationOperation
        exclude = ["created_at", "updated_at"]


class DeviceAssociationSerializer(BaseWritableNestedModelSerializer):
    """Device Association Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    device = DeviceReferenceSerializer(many=False, required=False)
    relationship = CodeableConceptSerializer(many=False, required=False)
    status = CodeableConceptSerializer(many=False, required=False)
    status_reason = CodeableConceptSerializer(many=False, required=False)
    subject = DeviceAssociationSubjectReferenceSerializer(many=False, required=False)
    body_structure = BodyStructureReferenceSerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)
    operation = DeviceAssociationOperationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceAssociation
        exclude = ["created_at", "updated_at"]
