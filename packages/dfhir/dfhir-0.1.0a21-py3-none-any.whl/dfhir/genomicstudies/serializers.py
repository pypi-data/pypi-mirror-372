"""genomic study serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    ReferenceSerializer,
)
from dfhir.conditions.serializers import (
    ConditionObservationCodeableReferenceSerializer,
)
from dfhir.devices.serializers import DeviceReferenceSerializer
from dfhir.documentreferences.serializers import DocumentReferenceReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.genomicstudies.models import (
    GenomicStudy,
    GenomicStudyAnalysis,
    GenomicStudyAnalysisDevice,
    GenomicStudyAnalysisInput,
    GenomicStudyAnalysisOutput,
    GenomicStudyAnalysisPerformer,
    GenomicStudyAnalysisPerformerActorReference,
    GenomicStudyAnalysisProtocolPerformedReference,
    GenomicStudyBasedOnReference,
    GenomicStudyReference,
    GenomicStudySubjectReference,
)
from dfhir.observations.serializers import (
    DocumentReferenceObservationReferenceSerializer,
)
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)
from dfhir.specimens.serializers import SpecimenReferenceSerializer


class GenomicStudyReferenceSerializer(BaseReferenceModelSerializer):
    """Genomic study reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudyReference
        exclude = ["created_at", "updated_at"]


class GenomicStudyAnalysisInputSerializer(WritableNestedModelSerializer):
    """Genomic study analysis input serializer."""

    file = DocumentReferenceReferenceSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)
    generated_by_identifier = IdentifierSerializer(many=False, required=False)
    generated_by_reference = GenomicStudyReferenceSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudyAnalysisInput
        exclude = ["created_at", "updated_at"]


class GenomicStudyAnalysisOutputSerializer(WritableNestedModelSerializer):
    """Genomic study analysis output serializer."""

    file = DocumentReferenceReferenceSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudyAnalysisOutput
        exclude = ["created_at", "updated_at"]


class GenomicStudyAnalysisPerformerActorReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Genomic study analysis performer actor reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudyAnalysisPerformerActorReference
        exclude = ["created_at", "updated_at"]


class GenomicStudyAnalysisPerformerSerializer(WritableNestedModelSerializer):
    """Genomic study analysis performer serializer."""

    actor = GenomicStudyAnalysisPerformerActorReferenceSerializer(
        many=False, required=False
    )
    role = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudyAnalysisPerformer
        exclude = ["created_at", "updated_at"]


class GenomicStudyAnalysisDeviceSerializer(WritableNestedModelSerializer):
    """Genomic study analysis device serializer."""

    device = DeviceReferenceSerializer(many=False, required=False)
    function = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudyAnalysisDevice
        exclude = ["created_at", "updated_at"]


class GenomicStudyAnalysisProtocolPerformedReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Genomic study analysis protocol performed serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudyAnalysisProtocolPerformedReference
        exclude = ["created_at", "updated_at"]


class GenomicStudyAnalysisSerializer(WritableNestedModelSerializer):
    """Genomic study analysis serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    method_type = CodeableConceptSerializer(many=True, required=False)
    change_type = CodeableConceptSerializer(many=True, required=False)
    genomic_build = CodeableConceptSerializer(many=False, required=False)
    focus = ReferenceSerializer(many=True, required=False)
    specimen = SpecimenReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    protocol_performed = GenomicStudyAnalysisProtocolPerformedReferenceSerializer(
        many=False, required=False
    )
    regions_studied = DocumentReferenceObservationReferenceSerializer(
        many=True, required=False
    )
    regions_called = DocumentReferenceObservationReferenceSerializer(
        many=True, required=False
    )
    input = GenomicStudyAnalysisInputSerializer(many=True, required=False)
    output = GenomicStudyAnalysisOutputSerializer(many=True, required=False)
    performer = GenomicStudyAnalysisPerformerSerializer(many=True, required=False)
    device = GenomicStudyAnalysisDeviceSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudyAnalysis
        exclude = ["created_at", "updated_at"]


class GenomicStudySubjectReferenceSerializer(BaseReferenceModelSerializer):
    """Genomic study subject reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudySubjectReference
        exclude = ["created_at", "updated_at"]


class GenomicStudyBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """Genomic study based on reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudyBasedOnReference
        exclude = ["created_at", "updated_at"]


class GenomicStudySerializer(BaseWritableNestedModelSerializer):
    """Genomic study serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    subject = GenomicStudySubjectReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    based_on = GenomicStudyBasedOnReferenceSerializer(many=True, required=False)
    referrer = PractitionerPractitionerRoleReferenceSerializer(
        many=False, required=False
    )
    interpreter = PractitionerPractitionerRoleReferenceSerializer(
        many=True, required=False
    )
    reason = ConditionObservationCodeableReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    analysis = GenomicStudyAnalysisSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = GenomicStudy
        exclude = ["created_at", "updated_at"]
