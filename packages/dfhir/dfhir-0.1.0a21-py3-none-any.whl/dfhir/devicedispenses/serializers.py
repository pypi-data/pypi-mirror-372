"""Devicedispenses serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    ReferenceSerializer,
    SimpleQuantitySerializer,
)

# from dfhir.devices.serializers import DeviceDeviceDefinitionCodeableReferenceSerializer
from dfhir.careplans.serializers import CarePlanDeviceRequestReferenceSerializer
from dfhir.detectedissues.serializers import DetectedIssueCodeableReferenceSerializer
from dfhir.devices.serializers import DeviceDeviceDefinitionCodeableReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.patients.serializers import PatientPractitionerReferenceSerializer
from dfhir.procedures.serializers import ProcedureReferenceSerializer
from dfhir.provenances.serializers import ProvenanceReferenceSerializer

from .models import (
    DeviceDispense,
    DeviceDispensePerformer,
    DeviceDispensePerformerActorReference,
    DeviceDispenseReceiverReference,
)

# from dfhir.detectedissues.serializers import DetectedIssueCodeableReferenceSerializer


class DeviceDispenseReceiverReferenceSerializer(BaseReferenceModelSerializer):
    """DeviceDispenseReceiverReference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDispenseReceiverReference
        exclude = ["created_at", "updated_at"]


class DeviceDispensePerformerActorReferenceSerializer(BaseReferenceModelSerializer):
    """DeviceDispensePerformerActorReference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDispensePerformerActorReference
        exclude = ["created_at", "updated_at"]


class DeviceDispensePerformerSerializer(WritableNestedModelSerializer):
    """DeviceDispensePerformer serializer."""

    function = CodeableConceptSerializer(many=False, required=False)
    actor = DeviceDispensePerformerActorReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDispensePerformer
        exclude = ["created_at", "updated_at"]


class DeviceDispenseSerializer(BaseWritableNestedModelSerializer):
    """DeviceDispense serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = CarePlanDeviceRequestReferenceSerializer(many=True, required=False)
    part_of = ProcedureReferenceSerializer(many=True, required=False)
    status_reason = DetectedIssueCodeableReferenceSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    device = DeviceDeviceDefinitionCodeableReferenceSerializer(
        many=False, required=False
    )
    subject = PatientPractitionerReferenceSerializer(many=False, required=False)
    receiver = DeviceDispenseReceiverReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    supporting_information = ReferenceSerializer(many=True, required=False)
    performer = DeviceDispensePerformerSerializer(many=True, required=False)
    location = LocationReferenceSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    destination = LocationReferenceSerializer(many=False, required=False)
    note = AnnotationSerializer(many=True, required=False)
    event_history = ProvenanceReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DeviceDispense
        exclude = ["created_at", "updated_at"]
