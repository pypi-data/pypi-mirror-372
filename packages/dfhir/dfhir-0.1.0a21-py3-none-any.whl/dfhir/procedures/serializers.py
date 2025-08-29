"""Procedures serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    RangeSerializer,
    ReferenceSerializer,
    TimingSerializer,
)
from dfhir.bodystructures.serializers import BodyStructureReferenceSerializer
from dfhir.conditions.serializers import ConditionCodeableReferenceSerializer
from dfhir.devices.serializers import DeviceReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.observations.serializers import ObservationCodeableReferenceSerializer
from dfhir.servicerequests.serializers import (
    ServiceRequestPlanDefinitionReferenceSerializer,
)

from .models import (
    Procedure,
    ProcedureBasedOnReference,
    ProcedureCodeableReference,
    ProcedureFocalDevice,
    ProcedureFocusReference,
    ProcedurePartOfReference,
    ProcedurePerformer,
    ProcedurePerformerActorReference,
    ProcedureReasonCodeableReference,
    ProcedureReasonReference,
    ProcedureRecorderReference,
    ProcedureReference,
    ProcedureReportedReference,
    ProcedureReportReference,
    ProcedureSubjectReference,
    ProcedureUsedCodeableReference,
    ProcedureUsedReference,
)


class ProcedureReportReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Report Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureReportReference
        exclude = ["created_at", "updated_at"]


class ProcedureBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Based On Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureBasedOnReference
        exclude = ["created_at", "updated_at"]


class ProcedurePartOfReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Part Of Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedurePartOfReference
        exclude = ["created_at", "updated_at"]


class ProcedureSubjectReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Subject Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureSubjectReference
        exclude = ["created_at", "updated_at"]


class ProcedureReportedReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Reported Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureReportedReference
        exclude = ["created_at", "updated_at"]


class ProcedureRecorderReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Recorder Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureRecorderReference
        exclude = ["created_at", "updated_at"]


class ProcedureReasonReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Reason Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureReasonReference
        exclude = ["created_at", "updated_at"]


class ProcedureUsedReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Used Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureUsedReference
        exclude = ["created_at", "updated_at"]


class ProcedureFocusReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Focus Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureFocusReference
        exclude = ["created_at", "updated_at"]


class ProcedurePerformerActorReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Performer Actor Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedurePerformerActorReference
        exclude = ["created_at", "updated_at"]


class ProcedureFocalDeviceSerializer(WritableNestedModelSerializer):
    """Procedure Focal Device serializer."""

    action = CodeableConceptSerializer(required=False)
    manipulated = DeviceReferenceSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureFocalDevice
        exclude = ["created_at", "updated_at"]


class ProcedurePerformerSerializer(WritableNestedModelSerializer):
    """Procedure Performer serializer."""

    function = CodeableConceptSerializer(required=False)
    actor = ProcedurePerformerActorReferenceSerializer(required=False)
    on_behalf_of = OrganizationReferenceSerializer(required=False)
    period = PeriodSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedurePerformer
        exclude = ["created_at", "updated_at"]


class ProcedureReasonCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Procedure Reason Codeable Reference serializer."""

    reference = ProcedureReasonReferenceSerializer(required=False)
    concept = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class ProcedureUsedCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Procedure Used Codeable Reference serializer."""

    reference = ProcedureUsedReferenceSerializer(required=False)
    concept = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureUsedCodeableReference
        exclude = ["created_at", "updated_at"]


class ProcedureSerializer(BaseWritableNestedModelSerializer):
    """Procedure serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = ProcedureBasedOnReferenceSerializer(many=True, required=False)
    part_of = ProcedurePartOfReferenceSerializer(many=True, required=False)
    status_reason = CodeableConceptSerializer(required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    code = CodeableConceptSerializer(required=False)
    subject = ProcedureSubjectReferenceSerializer(required=False)
    focus = ProcedureFocusReferenceSerializer(many=False, required=False)
    encounter = EncounterReferenceSerializer(required=False)
    occurrence_period = PeriodSerializer(required=False)
    occurrence_range = RangeSerializer(required=False)
    occurrence_timing = TimingSerializer(required=False)
    recorder = ProcedureRecorderReferenceSerializer(required=False)
    reported_reference = ProcedureReportedReferenceSerializer(required=False)
    performer = ProcedurePerformerSerializer(many=True, required=False)
    location = LocationReferenceSerializer(required=False, many=False)
    reason = ProcedureReasonCodeableReferenceSerializer(many=True, required=False)
    body_site = CodeableConceptSerializer(many=True, required=False)
    body_structure = BodyStructureReferenceSerializer(many=True, required=False)
    outcome = ObservationCodeableReferenceSerializer(many=True, required=False)
    report = ProcedureReportReferenceSerializer(many=True, required=False)
    complication = ConditionCodeableReferenceSerializer(many=True, required=False)
    follow_up = ServiceRequestPlanDefinitionReferenceSerializer(
        many=True, required=False
    )
    note = AnnotationSerializer(many=True, required=False)
    focal_device = ProcedureFocalDeviceSerializer(many=True, required=False)
    used = ProcedureUsedCodeableReferenceSerializer(many=True, required=False)
    supporting_info = ReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Procedure
        exclude = ["created_at", "updated_at"]


class ProcedureReferenceSerializer(BaseReferenceModelSerializer):
    """Procedure Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = ProcedureReference
        exclude = ["created_at", "updated_at"]


class ProcedureCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Procedure Codeable Reference serializer."""

    reference = ProcedureReferenceSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = ProcedureCodeableReference
        exclude = ["created_at", "updated_at"]
