"""medication statement serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    ReferenceSerializer,
    TimingSerializer,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.medications.serializers import MedicationCodeableReferenceSerializer
from dfhir.medicationstatements.models import (
    MedicationStatement,
    MedicationStatementAdherence,
    MedicationStatementInformationSourceReference,
    MedicationStatementPartOfReference,
    MedicationStatementReasonReference,
)
from dfhir.patients.serializers import PatientGroupReferenceSerializer


class MedicationStatementPartOfReferenceSerializer(BaseReferenceModelSerializer):
    """medication statement part of serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = MedicationStatementPartOfReference
        exclude = ["created_at", "updated_at"]


class MedicationStatementInformationSourceReferenceSerializer(
    BaseReferenceModelSerializer
):
    """medication statement information source reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = MedicationStatementInformationSourceReference
        exclude = ["created_at", "updated_at"]


class MedicationStatementReasonReferenceSerializer(BaseReferenceModelSerializer):
    """medication statement reason reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = MedicationStatementReasonReference
        exclude = ["created_at", "updated_at"]


class MedicationStatementAdherenceSerializer(WritableNestedModelSerializer):
    """medication statement adherence serializer."""

    code = CodeableConceptSerializer(required=False)
    reason = CodeableConceptSerializer(required=False)

    class Meta:
        """meta options."""

        model = MedicationStatementAdherence
        exclude = ["created_at", "updated_at"]


class MedicationStatementSerializer(BaseWritableNestedModelSerializer):
    """medication statement reference."""

    identifier = IdentifierSerializer(many=True, required=False)
    part_of = MedicationStatementPartOfReferenceSerializer(many=True, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    medication = MedicationCodeableReferenceSerializer(required=False)
    subject = PatientGroupReferenceSerializer(required=False)
    encounter = EncounterReferenceSerializer(required=False)
    effective_period = PeriodSerializer(required=False)
    effective_timing = TimingSerializer(required=False)
    information_source = MedicationStatementInformationSourceReferenceSerializer(
        many=True, required=False
    )
    derived_from = ReferenceSerializer(many=True, required=False)
    reason = MedicationStatementReasonReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    adherence = MedicationStatementAdherenceSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = MedicationStatement
        exclude = ["created_at", "updated_at"]
