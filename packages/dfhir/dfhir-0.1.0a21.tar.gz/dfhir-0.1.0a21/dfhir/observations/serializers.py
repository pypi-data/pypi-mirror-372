"""serializers file."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AnnotationSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
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
from dfhir.devices.serializers import DeviceDeviceMetricReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.molecularsequences.serializers import MolecularSequenceReferenceSerializer
from dfhir.observationdefinitions.serializers import (
    ObservationDefinitionReferenceSerializer,
)
from dfhir.patients.serializers import PatientGroupReferenceSerializer

from .models import (
    DocumentReferenceObservationReference,
    Observation,
    ObservationBasedOnReference,
    ObservationBodyStructureReference,
    ObservationCodeableReference,
    ObservationComponent,
    ObservationDerivedFromReference,
    ObservationHasMemberReference,
    ObservationPartOfReference,
    ObservationPerformerReference,
    ObservationReference,
    ObservationReferenceRange,
    ObservationSubjectReference,
    ObservationTriggeredBy,
    SampledData,
    SampledDataIntervalUnitCodes,
)


class ObservationReferenceSerializer(BaseReferenceModelSerializer):
    """observation reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = ObservationReference
        exclude = ["created_at", "updated_at"]


class ObservationBodyStructureReferenceSerializer(BaseReferenceModelSerializer):
    """observation body structure reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = ObservationBodyStructureReference
        exclude = ["created_at", "updated_at"]


class ObservationBasedOnReferenceSerializer(WritableNestedModelSerializer):
    """observation based on reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = ObservationBasedOnReference
        exclude = ["created_at", "updated_at"]


class ObservationPartOfReferenceSerializer(BaseReferenceModelSerializer):
    """observation part of reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = ObservationPartOfReference
        exclude = ["created_at", "updated_at"]


class ObservationSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """observation subject reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = ObservationSubjectReference
        exclude = ["created_at", "updated_at"]


class ObservationTriggeredBySerializer(BaseReferenceModelSerializer):
    """observation triggered by serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = ObservationTriggeredBy
        exclude = ["created_at", "updated_at"]


class ObservationHasMemberReferenceSerializer(BaseReferenceModelSerializer):
    """observation has member reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = ObservationHasMemberReference
        exclude = ["created_at", "updated_at"]


class ObservationDerivedFromReferenceSerializer(BaseReferenceModelSerializer):
    """observation derived from reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = ObservationDerivedFromReference
        exclude = ["created_at", "updated_at"]


class SampledDataIntervalUnitCodesSerializer(serializers.ModelSerializer):
    """sampled data interval unit codes serializer."""

    class Meta:
        """meta options."""

        model = SampledDataIntervalUnitCodes
        exclude = ["created_at", "updated_at"]


class SampledDataSerializer(WritableNestedModelSerializer):
    """sampled data serializer."""

    origin = QuantitySerializer(required=False, many=False)
    interval_unit = SampledDataIntervalUnitCodesSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = SampledData
        exclude = ["created_at", "updated_at"]


class ObservationPerformerReferenceSerializer(BaseReferenceModelSerializer):
    """observation performer reference serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = ObservationPerformerReference
        exclude = ["created_at", "updated_at"]


class ObservationReferenceRangeSerializer(WritableNestedModelSerializer):
    """observation reference range serializer."""

    low = QuantitySerializer(required=False, many=False)
    high = QuantitySerializer(required=False, many=False)
    normal_value = CodeableConceptSerializer(required=False, many=False)
    type = CodeableConceptSerializer(required=False, many=False)
    applies_to = CodeableConceptSerializer(required=False, many=True)
    age = RangeSerializer(required=False, many=True)

    class Meta:
        """meta options."""

        model = ObservationReferenceRange
        exclude = ["created_at", "updated_at"]


class ObservationComponentSerializer(WritableNestedModelSerializer):
    """observation component serializer."""

    code = CodeableConceptSerializer(required=False, many=False)
    value_quantity = QuantitySerializer(required=False, many=False)
    value_codeable_concept = CodeableConceptSerializer(required=False, many=False)
    value_range = RangeSerializer(required=False, many=False)
    value_ratio = RatioSerializer(required=False, many=False)
    value_sampled_data = SampledDataSerializer(required=False, many=False)
    value_period = PeriodSerializer(required=False, many=False)
    value_attachment = AttachmentSerializer(required=False, many=False)
    value_reference = MolecularSequenceReferenceSerializer(required=False, many=False)
    data_absent_reason = CodeableConceptSerializer(required=False, many=False)
    interpretation = CodeableConceptSerializer(required=False, many=True)
    reference_range = ObservationReferenceRangeSerializer(required=False, many=True)

    class Meta:
        """meta options."""

        model = ObservationComponent
        exclude = ["created_at", "updated_at"]


class ObservationSerializer(BaseWritableNestedModelSerializer):
    """observation serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    # TODO: instantiates_canonical = ObservationDefinitionReferenceSerializer()
    instantiates_reference = ObservationDefinitionReferenceSerializer(
        required=False, many=True
    )
    based_on = ObservationBasedOnReferenceSerializer(required=False, many=True)
    triggered_by = ObservationTriggeredBySerializer(required=False, many=True)
    part_of = ObservationPartOfReferenceSerializer(required=False, many=True)
    category = CodeableConceptSerializer(required=False, many=True)
    code = CodeableConceptSerializer(required=False, many=False)
    subject = ObservationSubjectReferenceSerializer(required=False, many=False)
    focus = ReferenceSerializer(required=False, many=True)
    encounter = EncounterReferenceSerializer(required=False, many=False)
    effective_period = PeriodSerializer(required=False, many=False)
    effective_timing = TimingSerializer(required=False, many=False)
    performer = ObservationPerformerReferenceSerializer(required=False, many=True)
    value_quantity = QuantitySerializer(required=False, many=False)
    value_codeable_concept = CodeableConceptSerializer(required=False, many=False)
    value_range = RangeSerializer(required=False, many=False)
    value_ratio = RatioSerializer(required=False, many=False)
    value_sampled_data = SampledDataSerializer(required=False, many=False)
    value_period = PeriodSerializer(required=False, many=False)
    value_attachment = AttachmentSerializer(required=False, many=False)
    value_reference = MolecularSequenceReferenceSerializer(required=False, many=False)
    data_absent_reason = CodeableConceptSerializer(required=False, many=False)
    interpretation = CodeableConceptSerializer(required=False, many=True)
    note = AnnotationSerializer(required=False, many=True)
    body_site = CodeableConceptSerializer(required=False, many=False)
    body_structure = BodyStructureReferenceSerializer(required=False, many=False)
    method = CodeableConceptSerializer(required=False, many=False)
    specimen = PatientGroupReferenceSerializer(required=False, many=False)
    device = DeviceDeviceMetricReferenceSerializer(required=False, many=False)
    reference_range = ObservationReferenceRangeSerializer(required=False, many=True)
    has_member = ObservationHasMemberReferenceSerializer(required=False, many=True)
    derived_from = ObservationDerivedFromReferenceSerializer(required=False, many=True)
    component = ObservationComponentSerializer(required=False, many=True)

    class Meta:
        """meta options."""

        model = Observation
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        """Validate serializer data."""
        validate_date_time_fields(
            data.get("effective_start_datetime"), data.get("effective_end_datetime")
        )
        return data


class ObservationCodeableReferenceSerializer(WritableNestedModelSerializer):
    """observation codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False, many=False)
    reference = ObservationReferenceSerializer(required=False, many=False)

    class Meta:
        """meta options."""

        model = ObservationCodeableReference
        exclude = ["created_at", "updated_at"]


class DocumentReferenceObservationReferenceSerializer(BaseReferenceModelSerializer):
    """Document Reference Observation Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta class."""

        model = DocumentReferenceObservationReference
        exclude = ["created_at", "updated_at"]
