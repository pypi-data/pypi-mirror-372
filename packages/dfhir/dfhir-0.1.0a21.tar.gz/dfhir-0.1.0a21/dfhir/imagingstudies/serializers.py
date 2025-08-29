"""imaging study serializers."""

from drf_writable_nested import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
)
from dfhir.bodystructures.serializers import BodyStructureCodeableReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.endpoints.serializers import EndpointReferenceSerializer
from dfhir.imagingstudies.models import (
    ImagingStudy,
    ImagingStudyBasedOnReference,
    ImagingStudyProcedureReference,
    ImagingStudyReasonReference,
    ImagingStudyReference,
    ImagingStudySeries,
    ImagingStudySeriesInstance,
    ImagingStudySeriesPerformer,
    ImagingStudySeriesPerformerActorReference,
    ImagingStudySubjectReference,
)
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)
from dfhir.specimens.serializers import SpecimenReferenceSerializer


class ImagingStudySubjectReferenceSerializer(BaseReferenceModelSerializer):
    """ImagingStudySubjectReferenceSerializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = ImagingStudySubjectReference
        exclude = ["created_at", "updated_at"]


class ImagingStudyBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """Imaging Study Based On Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = ImagingStudyBasedOnReference
        exclude = ["created_at", "updated_at"]


class ImagingStudyProcedureReferenceSerializer(BaseReferenceModelSerializer):
    """ImagingStudyProcedureReferenceSerializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = ImagingStudyProcedureReference
        exclude = ["created_at", "updated_at"]


class ImagingStudyReasonReferenceSerializer(BaseReferenceModelSerializer):
    """imaging study reason reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = ImagingStudyReasonReference
        exclude = ["created_at", "updated_at"]


class ImagingStudySeriesPerformerActorReferenceSerializer(BaseReferenceModelSerializer):
    """ImagingStudySeriesPerformerActorReferenceSerializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta."""

        model = ImagingStudySeriesPerformerActorReference
        exclude = ["created_at", "updated_at"]


class ImagingStudySeriesPerformerSerializer(WritableNestedModelSerializer):
    """ImagingStudySeriesPerformerSerializer."""

    function = CodeableConceptSerializer(required=False)
    actor = ImagingStudySeriesPerformerActorReferenceSerializer(required=False)

    class Meta:
        """Meta."""

        model = ImagingStudySeriesPerformer
        exclude = ["created_at", "updated_at"]


class ImagingStudySeriesInstanceSerializer(serializers.ModelSerializer):
    """imaging study series instance serializer."""

    class Meta:
        """meta."""

        model = ImagingStudySeriesInstance
        exclude = ["created_at", "updated_at"]


class ImagingStudySeriesSerializer(WritableNestedModelSerializer):
    """imaging study series serializer."""

    modality = CodeableConceptSerializer(required=False)
    endpoint = EndpointReferenceSerializer(required=False, many=True)
    body_site = BodyStructureCodeableReferenceSerializer(required=False)
    laterality = CodeableConceptSerializer(required=False)
    specimen = SpecimenReferenceSerializer(required=False, many=True)
    performer = ImagingStudySeriesPerformerSerializer(required=False, many=True)
    instance = ImagingStudySeriesInstanceSerializer(required=False, many=True)

    class Meta:
        """meta."""

        model = ImagingStudySeries
        exclude = ["created_at", "updated_at"]


class ImagingStudySerializer(BaseWritableNestedModelSerializer):
    """ImagingStudySerializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    modality = CodeableConceptSerializer(required=False, many=True)
    subject = ImagingStudySubjectReferenceSerializer(required=False)
    encounter = EncounterReferenceSerializer(required=False)
    based_on = ImagingStudyBasedOnReferenceSerializer(required=False, many=True)
    part_of = ImagingStudyBasedOnReferenceSerializer(required=False, many=True)
    referrer = PractitionerPractitionerRoleReferenceSerializer(required=False)
    endpoint = EndpointReferenceSerializer(required=False, many=True)
    procedure = ImagingStudyProcedureReferenceSerializer(required=False, many=True)
    location = LocationReferenceSerializer(required=False)
    reason = ImagingStudyReasonReferenceSerializer(required=False, many=True)
    note = AnnotationSerializer(required=False, many=True)
    series = ImagingStudySeriesSerializer(required=False, many=True)

    class Meta:
        """Meta."""

        model = ImagingStudy
        exclude = ["created_at", "updated_at"]


class ImagingStudyReferenceSerializer(BaseReferenceModelSerializer):
    """Imaging Selection Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = ImagingStudyReference
        exclude = ["created_at", "updated_at"]
