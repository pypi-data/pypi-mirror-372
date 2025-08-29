"""Detected issues serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    ReferenceSerializer,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)

from .models import (
    DetectedIssue,
    DetectedIssueAuthorReference,
    DetectedIssueCodeableReference,
    DetectedIssueEvidence,
    DetectedIssueMitigation,
    DetectedIssueReference,
    DetectedIssueSubjectReference,
)


class DetectedIssueReferenceSerializer(BaseReferenceModelSerializer):
    """detected Issue reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """meta options."""

        model = DetectedIssueReference
        exclude = ["created_at", "updated_at"]


class DetectedIssueCodeableReferenceSerializer(WritableNestedModelSerializer):
    """detected issue codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = DetectedIssueReferenceSerializer(required=False)

    class Meta:
        """meta options."""

        model = DetectedIssueCodeableReference
        exclude = ["created_at", "updated_at"]


class DetectedIssueSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """Detected Issue Subject Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = DetectedIssueSubjectReference
        exclude = ["created_at", "updated_at"]


class DetectedIssueAuthorReferenceSerializer(BaseReferenceModelSerializer):
    """Detected Issue Author Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = DetectedIssueAuthorReference
        exclude = ["created_at", "updated_at"]


class DetectedIssueEvidenceSerializer(BaseWritableNestedModelSerializer):
    """Detected Issue Evidence Serializer."""

    code = CodeableConceptSerializer(required=True, many=False)
    detail = ReferenceSerializer(required=False, many=True)

    class Meta:
        """Meta."""

        model = DetectedIssueEvidence
        exclude = ["created_at", "updated_at"]


class DetectedIssueMitigationSerializer(BaseWritableNestedModelSerializer):
    """Detected Issue Mitigation Serializer."""

    action = CodeableConceptSerializer(required=False, many=False)
    author = PractitionerPractitionerRoleReferenceSerializer(required=False, many=False)
    note = AnnotationSerializer(required=False, many=True)

    class Meta:
        """Meta."""

        model = DetectedIssueMitigation
        exclude = ["created_at", "updated_at"]


class DetectedIssueSerializer(BaseWritableNestedModelSerializer):
    """Detected Issue Serializer."""

    identifier = IdentifierSerializer(required=False, many=True)
    category = CodeableConceptSerializer(required=False, many=True)
    code = CodeableConceptSerializer(required=False, many=False)
    subject = DetectedIssueSubjectReferenceSerializer(required=False, many=False)
    encounter = EncounterReferenceSerializer(required=False, many=False)
    identified_period = PeriodSerializer(required=False, many=False)
    author = DetectedIssueAuthorReferenceSerializer(required=False, many=False)
    implicated = ReferenceSerializer(required=False, many=True)
    evidence = DetectedIssueEvidenceSerializer(required=False, many=True)
    mitigation = DetectedIssueMitigationSerializer(required=False, many=True)

    class Meta:
        """Meta."""

        model = DetectedIssue
        exclude = ["created_at", "updated_at"]
