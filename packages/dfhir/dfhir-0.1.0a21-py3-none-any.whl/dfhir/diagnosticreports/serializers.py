"""diagnostic reports serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AnnotationSerializer,
    AttachmentSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodeableReferenceSerializer,
    IdentifierSerializer,
    PeriodSerializer,
)
from dfhir.base.validators import validate_date_time_fields
from dfhir.communications.serializers import CommunicationReferenceSerializer
from dfhir.documentreferences.serializers import DocumentReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.observations.serializers import ObservationReferenceSerializer
from dfhir.specimens.serializers import SpecimenReferenceSerializer

from .models import (
    ConclusionCode,
    ConclusionCodeCodeableReference,
    ConclusionCodeReference,
    DiagnosticCategory,
    DiagnosticReport,
    DiagnosticReportBasedOnReference,
    DiagnosticReportCode,
    DiagnosticReportDocumentReferenceReference,
    DiagnosticReportMedia,
    DiagnosticReportPerformerReference,
    DiagnosticReportSubjectReference,
    SupportingInfo,
    SupportingInfoReference,
)

# TODO: from dfhir.observations.serializers import ObservationReferenceSerializer


class DiagnosticReportDocumentReferenceReferenceSerializer(
    BaseReferenceModelSerializer
):
    """diagnostic report document reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DiagnosticReportDocumentReferenceReference
        exclude = ["created_at", "updated_at"]


class DiagnosticReportBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """diagnostic report based on ref serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DiagnosticReportBasedOnReference
        exclude = ["created_at", "updated_at"]


class SubjectReferenceSerializer(BaseReferenceModelSerializer):
    """subject reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DiagnosticReportSubjectReference
        exclude = ["created_at", "updated_at"]


class DiagnosticReportMediaSerializer(WritableNestedModelSerializer):
    """diagnostic report media serializer."""

    link = DocumentReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = DiagnosticReportMedia
        exclude = ["created_at", "updated_at"]


class SupportingInfoReferenceSerializer(BaseReferenceModelSerializer):
    """supporting info reference serializer."""

    class Meta:
        """Meta class."""

        model = SupportingInfoReference
        exclude = ["created_at", "updated_at"]


class ConclusionCodeCodeableReferenceSerializer(WritableNestedModelSerializer):
    """conclusion code codeable reference serializer."""

    reference = CommunicationReferenceSerializer(many=False, required=False)
    concept = AttachmentSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ConclusionCodeCodeableReference
        exclude = ["created_at", "updated_at"]


class ConclusionCodeReferenceSerializer(BaseReferenceModelSerializer):
    """conclusion code reference serializer."""

    class Meta:
        """Meta class."""

        model = ConclusionCodeReference
        exclude = ["created_at", "updated_at"]


class DiagnosticReportPerformerSerializer(BaseReferenceModelSerializer):
    """diagnostic report performer serializer."""

    class Meta:
        """Meta class."""

        model = DiagnosticReportPerformerReference
        exclude = ["created_at", "updated_at"]


class SupportingInfoSerializer(WritableNestedModelSerializer):
    """diagnostic report supporting  serializer."""

    type = CodeableConceptSerializer(many=False, required=False)
    reference = SupportingInfoReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = SupportingInfo
        exclude = ["created_at", "updated_at"]


class DiagnosticReportSerializer(BaseWritableNestedModelSerializer):
    """diagnostic report serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = DiagnosticReportBasedOnReferenceSerializer(many=True, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    code = CodeableConceptSerializer(many=False, required=False)
    subject = SubjectReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(many=False, required=False)
    effective_period = PeriodSerializer(many=False, required=False)
    performer = DiagnosticReportPerformerSerializer(many=True, required=False)
    results_interpretation = DiagnosticReportPerformerSerializer(
        many=True, required=False
    )
    specimen = SpecimenReferenceSerializer(many=True, required=False)
    supporting_info = SupportingInfoSerializer(many=True, required=False)
    media = DiagnosticReportMediaSerializer(many=True, required=False)
    results = ObservationReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    conclusion_code = ConclusionCodeCodeableReferenceSerializer(
        many=True, required=False
    )
    recommendation = CodeableReferenceSerializer(many=True, required=False)
    presented_form = AttachmentSerializer(many=True, required=False)
    communication = CommunicationReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DiagnosticReport
        exclude = ["created_at", "updated_at"]

    def validate(self, data):
        """Validate data."""
        validate_date_time_fields(
            data.get("effective_start_datetime"), data.get("effective_end_datetime")
        )
        return data


class ConclusionCodeSerializer(serializers.ModelSerializer):
    """conclusion code serializer."""

    class Meta:
        """Meta class."""

        model = ConclusionCode
        exclude = ["created_at", "updated_at"]


class DiagnosticCategorySerializer(serializers.ModelSerializer):
    """diagnostic category serializer."""

    class Meta:
        """Meta class."""

        model = DiagnosticCategory
        exclude = ["created_at", "updated_at"]


class DiagnosticReportCodeSerializer(serializers.ModelSerializer):
    """diagnostic report code serializer."""

    class Meta:
        """Meta class."""

        model = DiagnosticReportCode
        exclude = ["created_at", "updated_at"]
