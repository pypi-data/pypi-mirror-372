"""Clinical impressions serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    ReferenceSerializer,
)
from dfhir.conditions.serializers import ConditionAllergyIntoleranceReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.patients.serializers import PatientGroupReferenceSerializer
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)

from .models import (
    ClinicalImpression,
    ClinicalImpressionFinding,
    ClinicalImpressionFindingItemCodeableReference,
    ClinicalImpressionFindingItemReference,
    ClinicalImpressionReference,
)


class ClinicalImpressionReferenceSerializer(BaseReferenceModelSerializer):
    """Clinical Impression Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ClinicalImpressionReference
        exclude = ["created_at", "updated_at"]


class ClinicalImpressionFindingItemReferenceSerializer(BaseReferenceModelSerializer):
    """Clinical Impression Finding Item Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ClinicalImpressionFindingItemReference
        exclude = ["created_at", "updated_at"]


class ClinicalImpressionFindingItemCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """Clinical Impression Finding Item Codeable Reference Serializer."""

    reference = ClinicalImpressionFindingItemReferenceSerializer(
        many=False, required=False
    )
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ClinicalImpressionFindingItemCodeableReference
        exclude = ["created_at", "updated_at"]


class ClinicalImpressionFindingSerializer(BaseWritableNestedModelSerializer):
    """Clinical Impression Finding Serializer."""

    item = ClinicalImpressionFindingItemCodeableReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """Meta class."""

        model = ClinicalImpressionFinding
        exclude = ["created_at", "updated_at"]


class ClinicalImpressionSerializer(BaseWritableNestedModelSerializer):
    """Clinical Impression Serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    status_reason = CodeableConceptSerializer(many=False, required=False)
    subject = PatientGroupReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    effective_period = PeriodSerializer(many=False, required=False)
    performer = PractitionerPractitionerRoleReferenceSerializer(
        many=False, required=False
    )
    previous = ClinicalImpressionReferenceSerializer(many=False, required=False)
    problem = ConditionAllergyIntoleranceReferenceSerializer(many=True, required=False)
    change_pattern = CodeableConceptSerializer(many=False, required=False)
    finding = ClinicalImpressionFindingSerializer(many=True, required=False)
    prognosis_codeable_concept = CodeableConceptSerializer(many=True, required=False)
    supporting_info = ReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = ClinicalImpression
        exclude = ["created_at", "updated_at"]
