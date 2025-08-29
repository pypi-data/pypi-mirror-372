"""immunization recommendation serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    ReferenceSerializer,
)
from dfhir.immunizationrecommendations.models import (
    ImmunizationRecommendation,
    ImmunizationRecommendationRecommendation,
    ImmunizationRecommendationRecommendationDateCriterion,
    ImmunizationRecommendationSupportingImmunizationReference,
)
from dfhir.patients.serializers import PatientReferenceSerializer


class ImmunizationRecommendationSupportingImmunizationReferenceSerializer(
    BaseReferenceModelSerializer
):
    """immunization recommendation  supporting immunization reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta class."""

        model = ImmunizationRecommendationSupportingImmunizationReference
        exclude = ["created_at", "updated_at"]


class ImmunizationRecommendationRecommendationDateCriterionSerializer(
    WritableNestedModelSerializer
):
    """immunization recommendation recommendation date criterion serializer."""

    code = CodeableConceptSerializer(required=False)

    class Meta:
        """meta class."""

        model = ImmunizationRecommendationRecommendationDateCriterion
        exclude = ["created_at", "updated_at"]


class ImmunizationRecommendationRecommendationSerializer(WritableNestedModelSerializer):
    """immunization recommendation recommendation serializer."""

    vaccine_code = CodeableConceptSerializer(many=True, required=False)
    target_disease = CodeableConceptSerializer(many=True, required=False)
    contraindicated_vaccine_code = CodeableConceptSerializer(many=True, required=False)
    forecast_status = CodeableConceptSerializer(required=False)
    forecast_reason = CodeableConceptSerializer(many=True, required=False)
    date_criterion = ImmunizationRecommendationRecommendationDateCriterionSerializer(
        required=False, many=True
    )
    supporting_information = (
        ImmunizationRecommendationSupportingImmunizationReferenceSerializer(
            required=False
        )
    )
    supporting_patient_information = ReferenceSerializer(many=True, required=False)

    class Meta:
        """meta class."""

        model = ImmunizationRecommendationRecommendation
        exclude = ["created_at", "updated_at"]


class ImmunizationRecommendationSerializer(BaseWritableNestedModelSerializer):
    """immunization recommendation serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    patient = PatientReferenceSerializer(many=False, required=True)
    authority = OrganizationReferenceSerializer(required=False)
    recommendation = ImmunizationRecommendationRecommendationSerializer(
        many=True, required=False
    )

    class Meta:
        """meta options."""

        model = ImmunizationRecommendation
        exclude = ["created_at", "updated_at"]
