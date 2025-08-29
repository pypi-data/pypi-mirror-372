"""service requests serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.activitydefinitions.serializers import (
    ActivityDefinitionPlanDefinitionCodeableReferenceSerializer,
)
from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    CodeableConceptSerializer,
    CodeableReferenceSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    QuantitySerializer,
    RangeSerializer,
    RatioSerializer,
    ReferenceSerializer,
    TimingSerializer,
)
from dfhir.base.validators import validate_date_time_fields
from dfhir.bodystructures.serializers import BodyStructureReferenceSerializer
from dfhir.coverages.serializers import CoverageClaimResponseReferenceSerializer
from dfhir.documentreferences.serializers import DocumentReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import LocationCodeableReferenceSerializer
from dfhir.provenances.serializers import ProvenanceReferenceSerializer

from .models import (
    AsNeeded,
    BodySite,
    OrderDetailParameter,
    OrderDetailParameterFocusCodeableReference,
    OrderDetailParameterFocusReference,
    Parameter,
    ProcedureCodes,
    ProcedureReason,
    ServiceRequest,
    ServiceRequestBasedOnReference,
    ServiceRequestCategory,
    ServiceRequestOrderDetail,
    ServiceRequestPatientInstruction,
    ServiceRequestPerformerReference,
    ServiceRequestPlanDefinitionReference,
    ServiceRequestPlanDefinitionReferenceCodeableReference,
    ServiceRequestReasonCodeableReference,
    ServiceRequestReasonReference,
    ServiceRequestReference,
    ServiceRequestRequesterReference,
    ServiceRequestSubjectReference,
)


class ServiceRequestPlanDefinitionReferenceSerializer(BaseReferenceModelSerializer):
    """service request plan definition reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ServiceRequestPlanDefinitionReference
        exclude = ["created_at", "updated_at"]


class ServiceRequestPlanDefinitionReferenceCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """service request plan definition reference codeable reference serializer."""

    concept = CodeableConceptSerializer(many=False, required=False)
    reference = ServiceRequestPlanDefinitionReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """meta options."""

        model = ServiceRequestPlanDefinitionReferenceCodeableReference
        exclude = ["created_at", "updated_at"]


class ServiceRequestBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """service request based on reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ServiceRequestBasedOnReference
        exclude = ["created_at", "updated_at"]


class OrderDetailParameterFocusReferenceSerializer(BaseReferenceModelSerializer):
    """order detail parameter focus reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = OrderDetailParameterFocusReference
        exclude = ["created_at", "updated_at"]


class OrderDetailParameterFocusCodeableReferenceSerializer(
    WritableNestedModelSerializer
):
    """order detail parameter focus codeable reference serializer."""

    concept = CodeableConceptSerializer(many=False, required=False)
    reference = OrderDetailParameterFocusReferenceSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = OrderDetailParameterFocusCodeableReference
        exclude = ["created_at", "updated_at"]


class OrderDetailParameterSerializer(WritableNestedModelSerializer):
    """order detail parameter serializer."""

    code = CodeableConceptSerializer(many=False, required=False)
    value_quantity = QuantitySerializer(many=False, required=False)
    value_ratio = RatioSerializer(many=False, required=False)
    value_range = RangeSerializer(many=False, required=False)
    value_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    value_period = PeriodSerializer(many=False, required=False)
    focus = OrderDetailParameterFocusCodeableReferenceSerializer(
        many=False, required=False
    )

    class Meta:
        """meta options."""

        model = OrderDetailParameter
        exclude = ["created_at", "updated_at"]


class ServiceRequestOrderDetailSerializer(WritableNestedModelSerializer):
    """service request order detail serializer."""

    parameter_focus = OrderDetailParameterFocusCodeableReferenceSerializer(
        many=False, required=False
    )
    parameter = OrderDetailParameterSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = ServiceRequestOrderDetail
        exclude = ["created_at", "updated_at"]


class ServiceRequestPatientInstructionSerializer(WritableNestedModelSerializer):
    """service request patient instruction serializer."""

    instruction_reference = DocumentReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = ServiceRequestPatientInstruction
        exclude = ["created_at", "updated_at"]


class ServiceRequestSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """service request subject reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ServiceRequestSubjectReference
        exclude = ["created_at", "updated_at"]


class ServiceRequestRequesterReferenceSerializer(BaseReferenceModelSerializer):
    """service request requester reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ServiceRequestRequesterReference
        exclude = ["created_at", "updated_at"]


class ServiceRequestPerformerReferenceSerializer(BaseReferenceModelSerializer):
    """service request performer reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ServiceRequestPerformerReference
        exclude = ["created_at", "updated_at"]


class ServiceRequestReasonReferenceSerializer(BaseReferenceModelSerializer):
    """service request reason reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ServiceRequestReasonReference
        exclude = ["created_at", "updated_at"]


class ServiceRequestReasonCodeableReferenceSerializer(WritableNestedModelSerializer):
    """service request reason codeable reference serializer."""

    concept = CodeableConceptSerializer(many=False, required=False)
    reference = ServiceRequestReasonReferenceSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ServiceRequestReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class ServiceRequestReferenceSerializer(BaseReferenceModelSerializer):
    """service request reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = ServiceRequestReference
        exclude = ["created_at", "updated_at"]


class ServiceRequestSerializer(WritableNestedModelSerializer):
    """service request serializer."""

    def get_fields(self):
        """Get fields."""
        from dfhir.specimens.serializers import SpecimenReferenceSerializer

        fields = super(ServiceRequestSerializer, self).get_fields()
        fields["specimen"] = SpecimenReferenceSerializer(many=True, required=False)

        return fields

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = ServiceRequestBasedOnReferenceSerializer(many=True, required=False)
    replace = ServiceRequestReferenceSerializer(many=True, required=False)
    requisition = IdentifierSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    code = ActivityDefinitionPlanDefinitionCodeableReferenceSerializer(required=False)
    order_detail = ServiceRequestOrderDetailSerializer(many=True, required=False)
    quantity_quantity = QuantitySerializer(many=False, required=False)
    quantity_ratio = RatioSerializer(many=False, required=False)
    quantity_range = RangeSerializer(many=False, required=False)
    subject = ServiceRequestSubjectReferenceSerializer(many=False, required=False)
    focus = ReferenceSerializer(many=True, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    occurrence_period = PeriodSerializer(many=False, required=False)
    occurrence_timing = TimingSerializer(many=False, required=False)
    as_needed_for = CodeableConceptSerializer(many=True, required=False)
    requester = ServiceRequestRequesterReferenceSerializer(many=False, required=False)
    additional_recipient = ServiceRequestRequesterReferenceSerializer(
        many=True, required=False
    )
    performer_type = CodeableConceptSerializer(many=False, required=False)
    performer = ServiceRequestPerformerReferenceSerializer(many=True, required=False)
    location = LocationCodeableReferenceSerializer(many=True, required=False)
    reason = ServiceRequestReasonCodeableReferenceSerializer(many=True, required=False)
    insurance = CoverageClaimResponseReferenceSerializer(required=False, many=True)
    supporting_info = CodeableReferenceSerializer(many=True, required=False)
    body_site = CodeableConceptSerializer(many=True, required=False)
    body_structure = BodyStructureReferenceSerializer(many=False, required=False)
    note = AnnotationSerializer(many=True, required=False)
    patient_instruction = ServiceRequestPatientInstructionSerializer(
        many=True, required=False
    )
    relevant_history = ProvenanceReferenceSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = ServiceRequest
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        """Service request serializer data validators."""
        validate_date_time_fields(
            data.get("start_date_time"), data.get("end_date_time")
        )
        return data


class ParameterSerializer(serializers.ModelSerializer):
    """parameter serializer class."""

    class Meta:
        """meta options."""

        model = Parameter
        exclude = ["created_at", "updated_at"]


class ServiceRequestCategorySerializer(serializers.ModelSerializer):
    """service request serializer."""

    class Meta:
        """meta options."""

        model = ServiceRequestCategory
        exclude = ["created_at", "updated_at"]


class AsNeededSerializer(serializers.ModelSerializer):
    """as needed serializer."""

    class Meta:
        """meta options."""

        model = AsNeeded
        exclude = ["created_at", "updated_at"]


class ProcedureReasonSerializer(serializers.ModelSerializer):
    """procedure reason serializer."""

    class Meta:
        """meta options."""

        model = ProcedureReason
        exclude = ["created_at", "updated_at"]


class BodySiteSerializer(serializers.ModelSerializer):
    """body site serializer."""

    class Meta:
        """meta options."""

        model = BodySite
        exclude = ["created_at", "updated_at"]


class ProcedureCodeSerializer(serializers.ModelSerializer):
    """procedure code serializer."""

    class Meta:
        """meta options."""

        model = ProcedureCodes
        exclude = ["created_at", "updated_at"]
