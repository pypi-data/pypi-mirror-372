"""medication dispense serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    QuantitySerializer,
    ReferenceSerializer,
)
from dfhir.careplans.serializers import CarePlanReferenceSerializer
from dfhir.detectedissues.serializers import DetectedIssueCodeableReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.medicationdispenses.models import (
    MedicationDispense,
    MedicationDispensePerformer,
    MedicationDispensePerformerActorReference,
    MedicationDispenseReceiverReference,
    MedicationDispenseSubstitution,
    MedicationDispenseSubstitutionResponsiblePartyReference,
)
from dfhir.medicationrequests.serializers import MedicationRequestReferenceSerializer
from dfhir.medications.serializers import MedicationCodeableReferenceSerializer
from dfhir.patients.serializers import PatientGroupReferenceSerializer
from dfhir.procedures.serializers import ProcedureReferenceSerializer
from dfhir.provenances.serializers import ProvenanceSerializer


class MedicationDispensePerformerActorReferenceSerializer(BaseReferenceModelSerializer):
    """medication dispense performer actor reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationDispensePerformerActorReference
        exclude = ["created_at", "updated_at"]


class MedicationDispensePerformerSerializer(WritableNestedModelSerializer):
    """medication dispense performer serializer."""

    function = CodeableConceptSerializer(many=False, required=False)
    actor = MedicationDispensePerformerActorReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """meta options."""

        model = MedicationDispensePerformer
        exclude = ["created_at", "updated_at"]


class MedicationDispenseReceiverReferenceSerializer(BaseReferenceModelSerializer):
    """medication dispense receiver reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationDispenseReceiverReference
        exclude = ["created_at", "updated_at"]


class MedicationDispenseSubstitutionResponsiblePartyReferenceSerializer(
    BaseReferenceModelSerializer
):
    """medication dispense substitution responsible party reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationDispenseSubstitutionResponsiblePartyReference
        exclude = ["created_at", "updated_at"]


class MedicationDispenseSubstitutionSerializer(WritableNestedModelSerializer):
    """medication dispense substitution serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    reason = CodeableConceptSerializer(many=True, required=False)
    responsible_party = (
        MedicationDispenseSubstitutionResponsiblePartyReferenceSerializer(
            many=True, required=False
        )
    )

    class Meta:
        """meta options."""

        model = MedicationDispenseSubstitution
        exclude = ["created_at", "updated_at"]


class MedicationDispenseSerializer(BaseWritableNestedModelSerializer):
    """medication dispense serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = CarePlanReferenceSerializer(many=True, required=False)
    part_of = ProcedureReferenceSerializer(many=True, required=False)
    not_performed_reason = DetectedIssueCodeableReferenceSerializer(
        many=False, required=False
    )
    category = CodeableConceptSerializer(many=True, required=False)
    medication = MedicationCodeableReferenceSerializer(many=False, required=False)
    subject = PatientGroupReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    supporting_information = ReferenceSerializer(many=True, required=False)
    performer = MedicationDispensePerformerSerializer(many=True, required=False)
    location = LocationReferenceSerializer(many=False, required=False)
    authorizing_prescription = MedicationRequestReferenceSerializer(
        many=True, required=False
    )
    type = CodeableConceptSerializer(many=False, required=False)
    quantity = QuantitySerializer(many=False, required=False)
    days_supply = QuantitySerializer(many=False, required=False)
    destination = LocationReferenceSerializer(many=False, required=False)
    receiver = MedicationDispenseReceiverReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    substitution = MedicationDispenseSubstitutionSerializer(many=False, required=False)
    event_history = ProvenanceSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = MedicationDispense
        exclude = ["created_at", "updated_at"]
