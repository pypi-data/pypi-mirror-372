"""Allergy intolerance serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AgeSerializer,
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    RangeSerializer,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.observations.serializers import ObservationCodeableReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer

# from dfhir.observations.serializers import ObservationCodeableReferenceSerializer
from .models import (
    AllergyIntolerance,
    AllergyIntoleranceAsserterReference,
    AllergyIntoleranceReaction,
    AllergyIntoleranceRecorderReference,
    AllergyIntoleranceReference,
)


class AllergyIntoleranceReferenceSerializer(BaseReferenceModelSerializer):
    """Allergy Intolerance Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = AllergyIntoleranceReference
        exclude = ["created_at", "updated_at"]


class AllergyIntoleranceRecorderReferenceSerializer(BaseReferenceModelSerializer):
    """Allergy Intolerance Recorder Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = AllergyIntoleranceRecorderReference
        exclude = ["created_at", "updated_at"]


class AllergyIntoleranceAsserterReferenceSerializer(BaseReferenceModelSerializer):
    """Allergy Intolerance Asserter Reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta options."""

        model = AllergyIntoleranceAsserterReference
        exclude = ["created_at", "updated_at"]


class AllergyIntoleranceReactionSerializer(WritableNestedModelSerializer):
    """Allergy Intolerance Reaction serializer."""

    substance = CodeableConceptSerializer(many=False, required=False)
    manifestation = ObservationCodeableReferenceSerializer(many=True, required=False)
    exposure_route = CodeableConceptSerializer(many=False, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = AllergyIntoleranceReaction
        exclude = ["created_at", "updated_at"]


class AllergyIntoleranceSerializer(WritableNestedModelSerializer):
    """Allergy Intolerance serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    clinical_status = CodeableConceptSerializer(many=False, required=False)
    verification_status = CodeableConceptSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    onset_age = AgeSerializer(many=False, required=False)
    onset_period = PeriodSerializer(many=False, required=False)
    onset_range = RangeSerializer(many=False, required=False)
    recorder = AllergyIntoleranceRecorderReferenceSerializer(many=False, required=False)
    asserter = AllergyIntoleranceAsserterReferenceSerializer(many=False, required=False)
    note = AnnotationSerializer(many=True, required=False)
    reaction = AllergyIntoleranceReactionSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = AllergyIntolerance
        exclude = ["created_at", "updated_at"]
