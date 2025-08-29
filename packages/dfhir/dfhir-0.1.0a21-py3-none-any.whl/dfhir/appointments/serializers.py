"""Appointment serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodingSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    ReferenceSerializer,
    VirtualServiceDetailsSerializer,
)
from dfhir.healthcareservices.serializers import (
    HealthCareServiceCodeableReferenceSerializer,
)
from dfhir.patients.serializers import (
    PatientGroupReferenceSerializer,
)
from dfhir.slots.serializers import SlotReferenceSerializer

from .models import (
    Appointment,
    AppointmentBasedOnReference,
    AppointmentEncounterReason,
    AppointmentParticipant,
    AppointmentParticipantActor,
    AppointmentReasonCodeableReference,
    AppointmentReasonReference,
    AppointmentReference,
    DocumentReferenceBinaryCommunicationReference,
    MonthlyTemplate,
    RecurrenceTemplate,
    WeeklyTemplate,
    YearlyTemplate,
)


class AppointmentReferenceSerializer(BaseReferenceModelSerializer):
    """Appointment reference serializer."""

    class Meta:
        """Meta class."""

        model = AppointmentReference
        exclude = ["created_at", "updated_at"]


class AppointmentBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """Care Plan DeviceRequest MedicationRequest ServiceRequest Request Orchestration Nutrition Order Visual Prescripsion Immunization Recommendation Reference serializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = AppointmentBasedOnReference
        exclude = ["created_at", "updated_at"]


class AppointmentReasonReferenceSerializer(BaseReferenceModelSerializer):
    """Condition Procedure Observation Immunization Recommendation Reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AppointmentReasonReference
        exclude = ["created_at", "updated_at"]


class AppointmentReasonCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Condition Procedure Observation Immunization Recommendation Codedable Reference serializer."""

    reference = AppointmentReasonReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = AppointmentReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class DocumentReferenceBinaryCommunicationReferenceSerializer(
    BaseReferenceModelSerializer
):
    """Document Reference Binary Communication Reference serializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = DocumentReferenceBinaryCommunicationReference
        exclude = ["created_at", "updated_at"]


class WeeklyTemplateSerializer(serializers.ModelSerializer):
    """Weekly template serializer."""

    class Meta:
        """Meta class."""

        model = WeeklyTemplate
        exclude = ["created_at", "updated_at"]


class YearlyTemplateSerializer(serializers.ModelSerializer):
    """Yearly template serializer."""

    class Meta:
        """Meta class."""

        model = YearlyTemplate
        exclude = [
            "created_at",
            "updated_at",
        ]


class MonthlyTemplateSerializer(WritableNestedModelSerializer):
    """Monthly template serializer."""

    day_of_week = CodingSerializer(required=False)
    nth_week_of_month = CodingSerializer(required=False)

    class Meta:
        """Meta class."""

        model = MonthlyTemplate
        exclude = ["created_at", "updated_at"]


class RecurrenceTemplateSerializer(WritableNestedModelSerializer):
    """Recurrence template serializer."""

    weekly_template = WeeklyTemplateSerializer(required=False)
    monthly_template = MonthlyTemplateSerializer(required=False)
    time_zone = CodeableConceptSerializer(required=False)
    recurrence_type = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta class."""

        model = RecurrenceTemplate
        exclude = ["created_at", "updated_at"]


class AppointmentParticipantActorSerializer(BaseReferenceModelSerializer):
    """Appointment actor serializer."""

    identifier = IdentifierSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = AppointmentParticipantActor
        exclude = ["created_at", "updated_at"]


class AppointmentParticipantSerializer(WritableNestedModelSerializer):
    """Participant serializer."""

    actor = AppointmentParticipantActorSerializer(required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    period = PeriodSerializer(required=False)

    class Meta:
        """Meta class."""

        model = AppointmentParticipant
        exclude = ["created_at", "updated_at"]


class EncounterReasonSerializer(serializers.ModelSerializer):
    """Encounter reason serializer."""

    class Meta:
        """Meta class."""

        model = AppointmentEncounterReason
        exclude = ["created_at", "updated_at"]


class AppointmentSerializer(BaseWritableNestedModelSerializer):
    """Appointment serializer."""

    def get_fields(self):
        """Get fields."""
        from dfhir.accounts.serializers import AccountReferenceSerializer

        fields = super().get_fields()
        fields["account"] = AccountReferenceSerializer(many=True, required=False)
        return fields

    identifier = IdentifierSerializer(many=True, required=False)
    cancellation_reason = CodeableConceptSerializer(required=False)
    klass = CodeableConceptSerializer(many=True, required=False)
    service_category = CodeableConceptSerializer(many=True, required=False)
    service_type = HealthCareServiceCodeableReferenceSerializer(
        many=True, required=False
    )
    specialty = CodeableConceptSerializer(many=True, required=False)
    appointment_type = CodeableConceptSerializer(required=False)
    reason = AppointmentReasonCodeableReferenceSerializer(many=True, required=False)
    priority = CodeableConceptSerializer(required=False)
    replaces = AppointmentReferenceSerializer(many=True, required=False)
    virtual_service = VirtualServiceDetailsSerializer(many=True, required=False)
    supporting_information = ReferenceSerializer(many=True, required=False)
    previous_appointment = AppointmentReferenceSerializer(required=False)
    originating_appointment = AppointmentReferenceSerializer(required=False)
    requested_period = PeriodSerializer(many=True, required=False)
    slot = SlotReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    patient_instruction = DocumentReferenceBinaryCommunicationReferenceSerializer(
        many=True, required=False
    )
    based_on = AppointmentBasedOnReferenceSerializer(many=True, required=False)
    subject = PatientGroupReferenceSerializer(required=False)
    recurrence_template = RecurrenceTemplateSerializer(many=True, required=False)
    participant = AppointmentParticipantSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = Appointment
        exclude = ["created_at", "updated_at"]
        rename_fields = {
            "class": "klass",
        }

    # def validate(self, data):
    #     """Validate date time fields."""
    #     validate_date_time_fields(
    #         data.get("requested_start_date"), data.get("requested_end_date")
    #     )
    #     return data
