"""immunization serializers."""

from dfhir.base.serializers import (
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
)
from dfhir.immunizationevaluations.models import ImmunizationEvaluation
from dfhir.immunizations.serializers import ImmunizationReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer


class ImmunizationEvaluationSerializer(BaseWritableNestedModelSerializer):
    """immunization evaluation serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    patient = PatientReferenceSerializer(many=False, required=False)
    authority = OrganizationReferenceSerializer(many=False, required=False)
    target_disease = CodeableConceptSerializer(many=False, required=False)
    immunization_event = ImmunizationReferenceSerializer(required=False)
    dose_status = CodeableConceptSerializer(many=False, required=False)
    dose_status_reason = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """meta class."""

        model = ImmunizationEvaluation
        exclude = ["created_at", "updated_at"]
