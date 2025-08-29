"""risk assessment serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    RangeSerializer,
    ReferenceSerializer,
)
from dfhir.conditions.serializers import ConditionReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.patients.serializers import PatientGroupReferenceSerializer
from dfhir.riskassessments.models import (
    RiskAssessment,
    RiskAssessmentPerformerReference,
    RiskAssessmentPrediction,
    RiskAssessmentReasonCodeableConcept,
    RiskAssessmentReasonReference,
)


class RiskAssessmentPredictionSerializer(WritableNestedModelSerializer):
    """risk assessment prediction serializer."""

    outcome = CodeableConceptSerializer(required=False)
    probability_range = RangeSerializer(required=False)
    qualitative_risk = CodeableConceptSerializer(required=False)
    when_period = PeriodSerializer(required=False)
    when_range = RangeSerializer(required=False)

    class Meta:
        """Meta."""

        model = RiskAssessmentPrediction
        exclude = ["created_at", "updated_at"]


class RiskAssessmentPerformerReferenceSerializer(WritableNestedModelSerializer):
    """risk assessment performer reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = RiskAssessmentPerformerReference
        exclude = ["created_at", "updated_at"]


class RiskAssessmentReasonReferenceSerializer(BaseReferenceModelSerializer):
    """risk assessment reason reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = RiskAssessmentReasonReference
        exclude = ["created_at", "updated_at"]


class RiskAssessmentReasonCodeableReferenceSerializer(WritableNestedModelSerializer):
    """risk assessment reason codeable concept serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = RiskAssessmentReasonReferenceSerializer(required=False)

    class Meta:
        """Meta."""

        model = RiskAssessmentReasonCodeableConcept
        exclude = ["created_at", "updated_at"]


class RiskAssessmentSerializer(BaseWritableNestedModelSerializer):
    """risk assessment serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    based_on = ReferenceSerializer(required=False)
    parent = ReferenceSerializer(required=False)
    method = CodeableConceptSerializer(required=False)
    code = CodeableConceptSerializer(required=False)
    subject = PatientGroupReferenceSerializer(required=False)
    encounter = EncounterReferenceSerializer(required=False)
    occurrence_period = PeriodSerializer(required=False)
    condition = ConditionReferenceSerializer(required=False)
    performer = RiskAssessmentPerformerReferenceSerializer(required=False)
    reason = RiskAssessmentReasonCodeableReferenceSerializer(required=False)
    basis = ReferenceSerializer(required=False, many=True)
    prediction = RiskAssessmentPredictionSerializer(required=False, many=True)
    note = AnnotationSerializer(required=False, many=True)

    class Meta:
        """Meta options."""

        model = RiskAssessment
        exclude = ["created_at", "updated_at"]
