"""Encounter serializers file."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.appointments.serializers import AppointmentReferenceSerializer
from dfhir.base.serializers import (
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    VirtualServiceDetailsSerializer,
)
from dfhir.base.serializers import (
    QuantitySerializer as DurationSerializer,
)
from dfhir.careteams.serializers import CareTeamReferenceSerializer
from dfhir.conditions.serializers import ConditionCodeableReferenceSerializer
from dfhir.healthcareservices.serializers import (
    HealthCareServiceCodeableReferenceSerializer,
)
from dfhir.locations.serializers import (
    LocationOrganizationReferenceSerializer,
    LocationReferenceSerializer,
)
from dfhir.patients.serializers import PatientGroupReferenceSerializer

from .models import (
    DietPreference,
    Encounter,
    EncounterAdmission,
    EncounterBasedOnReference,
    EncounterCondition,
    EncounterDiagnosis,
    EncounterEpisodeOfCareReference,
    EncounterLocation,
    EncounterParticipant,
    EncounterParticipantActorReference,
    EncounterReason,
    EncounterReasonValueCodeableReference,
    EncounterReasonValueReference,
    EncounterReference,
    SpecialArrangement,
    SpecialCourtesy,
)


class EncounterParticipantActorReferenceSerializer(BaseReferenceModelSerializer):
    """Encounter Participant Actor Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = EncounterParticipantActorReference
        exclude = ["created_at", "updated_at"]


class EncounterParticipantSerializer(WritableNestedModelSerializer):
    """Encounter Participant Serializer."""

    actor = EncounterParticipantActorReferenceSerializer(many=False, required=False)
    type = CodeableConceptSerializer(many=True, required=False)
    period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = EncounterParticipant
        exclude = ["created_at", "updated_at"]


class EncounterDiagnosisSerializer(WritableNestedModelSerializer):
    """Encounter Diagnosis Serializer."""

    use = CodeableConceptSerializer(many=True, required=False)
    condition = ConditionCodeableReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = EncounterDiagnosis
        exclude = ["created_at", "updated_at"]


class EncounterAdmissionSerializer(WritableNestedModelSerializer):
    """Encounter Admission Serializer."""

    pre_admission_identifier = IdentifierSerializer(many=False, required=False)
    origin = LocationOrganizationReferenceSerializer(many=False, required=False)
    admit_source = CodeableConceptSerializer(many=False, required=False)
    re_admission = CodeableConceptSerializer(many=False, required=False)
    destination = LocationOrganizationReferenceSerializer(many=False, required=False)
    discharge_disposition = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = EncounterAdmission
        exclude = ["created_at", "updated_at"]


class EncounterLocationSerializer(WritableNestedModelSerializer):
    """Encounter Location Serializer."""

    location = LocationReferenceSerializer(many=False, required=False)
    form = CodeableConceptSerializer(many=False, required=False)
    period = PeriodSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = EncounterLocation
        exclude = ["created_at", "updated_at"]


class EncounterBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """Encounter Based On Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = EncounterBasedOnReference
        exclude = ["created_at", "updated_at"]


class EncounterReferenceSerializer(BaseReferenceModelSerializer):
    """Encounter Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = EncounterReference
        exclude = ["created_at", "updated_at"]


class EncounterReasonValueReferenceSerializer(BaseReferenceModelSerializer):
    """Encounter Reason Value Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = EncounterReasonValueReference
        exclude = ["created_at", "updated_at"]


class EncounterReasonValueCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Encounter Reason Value Codeable Reference Serializer."""

    reference = EncounterReasonValueReferenceSerializer(many=False, required=False)
    concept = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """Meta class."""

        model = EncounterReasonValueCodeableReference
        exclude = ["created_at", "updated_at"]


class EncounterReasonSerializer(WritableNestedModelSerializer):
    """Encounter Reason Serializer."""

    use = CodeableConceptSerializer(many=True, required=False)
    value = EncounterReasonValueCodeableReferenceSerializer(many=True, required=False)

    class Meta:
        """Meta class."""

        model = EncounterReason
        exclude = ["created_at", "updated_at"]


class EncounterConditionSerializer(serializers.ModelSerializer):
    """Encounter Condition Serializer."""

    class Meta:
        """Meta class."""

        model = EncounterCondition
        exclude = ["created_at", "updated_at"]


class SpecialCourtesySerializer(serializers.ModelSerializer):
    """Encounter Specialty Serializer."""

    class Meta:
        """Meta class."""

        model = SpecialCourtesy
        exclude = ["created_at", "updated_at"]


class DietPreferenceSerializer(serializers.ModelSerializer):
    """Diet Preference Serializer."""

    class Meta:
        """Meta class."""

        model = DietPreference
        exclude = ["created_at", "updated_at"]


class SpecialArrangementSerializer(serializers.ModelSerializer):
    """Special Arrangement Serializer."""

    class Meta:
        """Meta class."""

        model = SpecialArrangement
        exclude = ["created_at", "updated_at"]


class EncounterSerializer(BaseWritableNestedModelSerializer):
    """Encounter Serializer."""

    def get_fields(self):
        """Get fields."""
        from dfhir.accounts.serializers import AccountReferenceSerializer
        from dfhir.episodeofcares.serializers import EpisodeOfCareReferenceSerializer

        fields = super().get_fields()

        fields["account"] = AccountReferenceSerializer(required=False, many=True)
        fields["episode_of_care"] = EpisodeOfCareReferenceSerializer(
            required=False, many=True
        )
        return fields

    identifier = IdentifierSerializer(required=False, many=True)
    klass = CodeableConceptSerializer(required=False, many=True)
    priority = CodeableConceptSerializer(required=False)
    type = CodeableConceptSerializer(required=False, many=True)
    service_type = HealthCareServiceCodeableReferenceSerializer(
        required=False, many=True
    )
    subject = PatientGroupReferenceSerializer(required=False)
    subject_status = CodeableConceptSerializer(required=False)
    based_on = EncounterBasedOnReferenceSerializer(required=False, many=True)
    care_team = CareTeamReferenceSerializer(required=False, many=True)
    part_of = EncounterReferenceSerializer(required=False, many=True)
    service_provider = OrganizationReferenceSerializer(required=False)
    participant = EncounterParticipantSerializer(required=False, many=True)
    appointment = AppointmentReferenceSerializer(required=False, many=True)
    virtual_service = VirtualServiceDetailsSerializer(required=False, many=True)
    actual_period = PeriodSerializer(required=False)
    length = DurationSerializer(required=False)
    reason = EncounterReasonSerializer(required=False, many=True)
    diagnosis = EncounterDiagnosisSerializer(required=False, many=True)
    diet_preference = CodeableConceptSerializer(required=False, many=True)
    special_arrangement = CodeableConceptSerializer(required=False, many=True)
    special_courtesy = CodeableConceptSerializer(required=False, many=True)
    admission = EncounterAdmissionSerializer(required=False)
    location = EncounterLocationSerializer(required=False, many=True)

    class Meta:
        """Meta class."""

        model = Encounter
        exclude = ["created_at", "updated_at"]
        rename_fields = {
            "class": "klass",
        }


class EncounterEpisodeOfCareReferenceSerializer(BaseReferenceModelSerializer):
    """Encounter Episode Of Care Reference Serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta class."""

        model = EncounterEpisodeOfCareReference
        exclude = ["created_at", "updated_at"]
