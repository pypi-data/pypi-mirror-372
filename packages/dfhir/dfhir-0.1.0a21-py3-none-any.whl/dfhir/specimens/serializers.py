"""specimen serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    DurationSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    SimpleQuantitySerializer,
)
from dfhir.bodystructures.serializers import BodyStructureCodeableReferenceSerializer
from dfhir.devices.serializers import DeviceReferenceSerializer
from dfhir.procedures.serializers import ProcedureReferenceSerializer
from dfhir.servicerequests.serializers import ServiceRequestReferenceSerializer
from dfhir.specimens.models import (
    Specimen,
    SpecimenCollection,
    SpecimenCollectorReference,
    SpecimenContainer,
    SpecimenFeature,
    SpecimenProcessing,
    SpecimenProcessingPerformerReference,
    SpecimenReference,
    SpecimenSubjectReference,
)
from dfhir.substances.serializers import SubstanceReferenceSerializer


class SpecimenReferenceSerializer(BaseReferenceModelSerializer):
    """specimen reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta class."""

        model = SpecimenReference
        exclude = ["created_at", "updated_at"]


class SpecimenFeatureSerializer(WritableNestedModelSerializer):
    """specimen feature serializer."""

    type = CodeableConceptSerializer(required=False)

    class Meta:
        """meta class."""

        model = SpecimenFeature
        exclude = ["created_at", "updated_at"]


class SpecimenCollectorReferenceSerializer(BaseReferenceModelSerializer):
    """specimen collector reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta class."""

        model = SpecimenCollectorReference
        exclude = ["created_at", "updated_at"]


class SpecimenCollectionSerializer(WritableNestedModelSerializer):
    """specimen collection serializer."""

    collector = SpecimenCollectorReferenceSerializer(many=False, required=False)
    collected_period = PeriodSerializer(many=False, required=False)
    duration = DurationSerializer(many=False, required=False)
    quantity = SimpleQuantitySerializer(many=False, required=False)
    method = CodeableConceptSerializer(many=False, required=False)
    device = DeviceReferenceSerializer(many=False, required=False)
    procedure = ProcedureReferenceSerializer(many=False, required=False)
    body_site = BodyStructureCodeableReferenceSerializer(many=False, required=False)
    fasting_status_codeable_concept = CodeableConceptSerializer(
        many=False, required=False
    )
    fasting_status_duration = DurationSerializer(many=False, required=False)

    class Meta:
        """meta class."""

        model = SpecimenCollection
        exclude = ["created_at", "updated_at"]


class SpecimenPerformerReferenceSerializer(BaseReferenceModelSerializer):
    """specimen performer reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta class."""

        model = SpecimenProcessingPerformerReference
        exclude = ["created_at", "updated_at"]


class SpecimenProcessingSerializer(WritableNestedModelSerializer):
    """specimen processing serializer."""

    method = CodeableConceptSerializer(many=False, required=False)
    performer = SpecimenPerformerReferenceSerializer(many=False, required=False)
    device = DeviceReferenceSerializer(many=False, required=False)
    additive = SubstanceReferenceSerializer(many=True, required=False)
    time_period = PeriodSerializer(many=False, required=False)
    time_duration = DurationSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = SpecimenProcessing
        exclude = ["created_at", "updated_at"]


class SpecimenContainerSerializer(WritableNestedModelSerializer):
    """specimen container serializer."""

    device = DeviceReferenceSerializer(many=False, required=False)
    specimen_quantity = SimpleQuantitySerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = SpecimenContainer
        exclude = ["created_at", "updated_at"]


class SpecimenSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """specimen subject reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = SpecimenSubjectReference
        exclude = ["created_at", "updated_at"]


class SpecimenSerializer(BaseWritableNestedModelSerializer):
    """specimen serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    accession_identifier = IdentifierSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    subject = SpecimenSubjectReferenceSerializer(many=False, required=False)
    parent = SpecimenReferenceSerializer(many=True, required=False)
    request = ServiceRequestReferenceSerializer(many=True, required=False)
    role = CodeableConceptSerializer(many=True, required=False)
    feature = SpecimenFeatureSerializer(many=True, required=False)
    collections = SpecimenCollectionSerializer(many=False, required=False)
    processing = SpecimenProcessingSerializer(many=True, required=False)
    container = SpecimenContainerSerializer(many=True, required=False)
    condition = CodeableConceptSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = Specimen
        exclude = ["created_at", "updated_at"]
