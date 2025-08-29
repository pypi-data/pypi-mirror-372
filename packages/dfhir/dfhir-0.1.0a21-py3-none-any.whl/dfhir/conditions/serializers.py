"""Serializers for Conditions."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AgeSerializer,
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodeableReferenceSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    RangeSerializer,
)
from dfhir.patients.serializers import PatientGroupReferenceSerializer

from .models import (
    Condition,
    ConditionAllergyIntoleranceReference,
    ConditionAsserterReference,
    ConditionCodeableReference,
    ConditionObservationCodeableReference,
    ConditionObservationReference,
    ConditionRecorderReference,
    ConditionReference,
    ConditionStage,
    ConditionStageAssessmentReference,
)


class ConditionObservationReferenceSerializer(BaseReferenceModelSerializer):
    """Condition Observation Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ConditionObservationReference
        exclude = ["created_at", "updated_at"]


class ConditionObservationCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Condition Observation Codeable Reference Serializer."""

    reference = ConditionObservationReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ConditionObservationCodeableReference
        exclude = ["created_at", "updated_at"]


class ConditionStageAssessmentReferenceSerializer(BaseReferenceModelSerializer):
    """Condition Stage Assessment Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ConditionStageAssessmentReference
        exclude = ["created_at", "updated_at"]


class ConditionStageSerializer(BaseWritableNestedModelSerializer):
    """Condition Stage Serializer."""

    summary = CodeableConceptSerializer(many=False, required=False)
    assessment = ConditionStageAssessmentReferenceSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ConditionStage
        exclude = ["created_at", "updated_at"]


class ConditionRecorderReferenceSerializer(BaseReferenceModelSerializer):
    """Condition Recorder Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ConditionRecorderReference
        exclude = ["created_at", "updated_at"]


class ConditionAsserterReferenceSerializer(BaseReferenceModelSerializer):
    """Condition Asserter Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ConditionAsserterReference
        exclude = ["created_at", "updated_at"]


class ConditionReferenceSerializer(BaseReferenceModelSerializer):
    """Condition Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ConditionReference
        exclude = ["created_at", "updated_at"]


class ConditionCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Condition Codeable Reference Serializer."""

    reference = ConditionReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ConditionCodeableReference
        exclude = ["created_at", "updated_at"]


class ConditionSerializer(BaseWritableNestedModelSerializer):
    """Condition Serializer."""

    # this method is used to resolve circular import issues with the EncounterReferenceSerializer
    def get_fields(self):
        """Get fields."""
        from dfhir.encounters.serializers import EncounterReferenceSerializer

        fields = super().get_fields()
        fields["encounter"] = EncounterReferenceSerializer(required=False, many=False)
        return fields

    identifier = IdentifierSerializer(many=True, required=False)
    clinical_status = CodeableConceptSerializer(many=False, required=False)
    verification_status = CodeableConceptSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    severity = CodeableConceptSerializer(many=False, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    body_site = CodeableConceptSerializer(many=True, required=False)
    subject = PatientGroupReferenceSerializer(many=False, required=False)
    onset_age = AgeSerializer(many=False, required=False)
    onset_period = PeriodSerializer(many=False, required=False)
    onset_range = RangeSerializer(many=False, required=False)
    abatement_age = AgeSerializer(many=False, required=False)
    abatement_period = PeriodSerializer(many=False, required=False)
    abatement_range = RangeSerializer(many=False, required=False)
    recorder = ConditionRecorderReferenceSerializer(many=False, required=False)
    asserter = ConditionAsserterReferenceSerializer(many=False, required=False)
    stage = ConditionStageSerializer(many=True, required=False)
    evidence = CodeableReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Condition
        exclude = ["created_at", "updated_at"]


class ConditionAllergyIntoleranceReferenceSerializer(BaseReferenceModelSerializer):
    """Condition Allergy Intolerance Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ConditionAllergyIntoleranceReference
        exclude = ["created_at", "updated_at"]
