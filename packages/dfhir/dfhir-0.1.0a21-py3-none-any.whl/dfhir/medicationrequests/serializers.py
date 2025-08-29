"""medicationrequests serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    PeriodSerializer,
    QuantitySerializer,
    ReferenceSerializer,
)
from dfhir.base.serializers import QuantitySerializer as DurationSerializer
from dfhir.devices.serializers import DeviceCodeableReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.medicationrequests.models import (
    AdditionalIllustration,
    DispenseRequest,
    DispenseRequestInitialFill,
    DosageMethod,
    DosageRoute,
    DosageSite,
    MedicationRequest,
    MedicationRequestBasedOnReference,
    MedicationRequestCategory,
    MedicationRequestInsuranceReference,
    MedicationRequestMedicationCode,
    MedicationRequestPerformerReference,
    MedicationRequestProvinanceReference,
    MedicationRequestReason,
    MedicationRequestReasonReference,
    MedicationRequestReference,
    MedicationRequestReferenceType,
    MedicationRequestRequesterReference,
    MedicationRequestSubstitution,
    MedicatonRequestReasonCodealbleReference,
    ReferenceAsNeededFor,
    medicationRequestInformationSourceReference,
)
from dfhir.medications.serializers import MedicationCodeableReferenceSerializer
from dfhir.patients.serializers import (
    PatientGroupReferenceSerializer as SubjectSerializer,
)
from dfhir.practitioners.serializers import (
    PractitionerPractitionerRoleReferenceSerializer,
)


class MedicationRequestBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """medication request based on reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = MedicationRequestBasedOnReference
        exclude = ["created_at", "updated_at"]


class MedicationRequestReferenceSerializer(BaseReferenceModelSerializer):
    """medication request reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = MedicationRequestReference
        exclude = ["created_at", "updated_at"]


class MedicationRequestInformationSourceReferenceSerializer(
    BaseReferenceModelSerializer
):
    """medication request information source reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = medicationRequestInformationSourceReference
        exclude = ["created_at", "updated_at"]


class MedicationRequestRequesterReferenceSerializer(BaseReferenceModelSerializer):
    """medication request requester reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = MedicationRequestRequesterReference
        exclude = ["created_at", "updated_at"]


class MedicationRequestPerformerReferenceSerializer(BaseReferenceModelSerializer):
    """medication request performer reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = MedicationRequestPerformerReference
        exclude = ["created_at", "updated_at"]


class MedicationRequestReasonReferenceSerializer(BaseReferenceModelSerializer):
    """medication request reason reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = MedicationRequestReasonReference
        exclude = ["created_at", "updated_at"]


class MedicatonRequestReasonCodealbleReferenceSerializer(WritableNestedModelSerializer):
    """medication request reason codeable reference serializer."""

    concept = CodeableConceptSerializer(many=False, required=False)
    reference = MedicationRequestReasonReferenceSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = MedicatonRequestReasonCodealbleReference
        exclude = ["created_at", "updated_at"]


class DispenseRequestInitialFillSerializer(serializers.ModelSerializer):
    """dispense request initial fill serializer."""

    quantity = QuantitySerializer(many=False, required=False)
    duration = DurationSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = DispenseRequestInitialFill
        exclude = ["created_at", "updated_at"]


class DispenseRequestSerializer(WritableNestedModelSerializer):
    """dispense request serializer."""

    initial_fill = DispenseRequestInitialFillSerializer(many=False, required=False)
    dispense_interval = DurationSerializer(many=False, required=False)
    validity_period = PeriodSerializer(many=False, required=False)
    quantity = QuantitySerializer(many=False, required=False)
    expected_supply_duration = DurationSerializer(many=False, required=False)
    dispenser = OrganizationReferenceSerializer(many=False, required=False)
    dispense_instruction = AnnotationSerializer(many=False, required=False)
    dose_administration = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = DispenseRequest
        exclude = ["created_at", "updated_at"]


class MedicationRequestSubstitutionSerializer(WritableNestedModelSerializer):
    """medication request substitution serializer."""

    allowed_codeable_concept = CodeableConceptSerializer(many=False, required=False)
    reason = CodeableConceptSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = MedicationRequestSubstitution
        exclude = ["created_at", "updated_at"]


class MedicationRequestInsuranceReferenceSerializer(BaseReferenceModelSerializer):
    """medication request insurance reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = MedicationRequestInsuranceReference
        exclude = ["created_at", "updated_at"]


class MedicationRequestProvinanceReferenceSerializer(BaseReferenceModelSerializer):
    """medication request provenance reference serializer."""

    identifier = IdentifierSerializer(many=False, required=False)

    class Meta:
        """metadata."""

        model = MedicationRequestProvinanceReference
        exclude = ["created_at", "updated_at"]


class MedicationRequestSerializer(BaseWritableNestedModelSerializer):
    """medication requests serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = MedicationRequestBasedOnReferenceSerializer(many=True, required=False)
    prior_prescription = MedicationRequestReferenceSerializer(
        many=False, required=False
    )
    group_identifier = IdentifierSerializer(many=False, required=False)
    status_reason = CodeableConceptSerializer(many=False, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    medication = MedicationCodeableReferenceSerializer(many=False, required=False)
    subject = SubjectSerializer(many=False, required=False)
    information_source = MedicationRequestInformationSourceReferenceSerializer(
        many=True, required=False
    )
    encounter = EncounterReferenceSerializer(many=False, required=False)
    supporting_information = ReferenceSerializer(many=True, required=False)
    requester = MedicationRequestRequesterReferenceSerializer(
        many=False, required=False
    )
    performer_type = CodeableConceptSerializer(many=False, required=False)
    performer = MedicationRequestPerformerReferenceSerializer(
        many=False, required=False
    )
    device = DeviceCodeableReferenceSerializer(many=True, required=False)
    recorder = PractitionerPractitionerRoleReferenceSerializer(
        many=False, required=False
    )
    reason = MedicatonRequestReasonCodealbleReferenceSerializer(
        many=True, required=False
    )
    course_of_therapy_type = CodeableConceptSerializer(many=False, required=False)
    insurance = MedicationRequestInsuranceReferenceSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    effective_dose_period = PeriodSerializer(many=False, required=False)
    dispense_request = DispenseRequestSerializer(many=False, required=False)
    substitution = MedicationRequestSubstitutionSerializer(many=False, required=False)
    event_history = MedicationRequestProvinanceReferenceSerializer(
        many=True, required=False
    )

    class Meta:
        """metadata."""

        model = MedicationRequest
        exclude = ["created_at", "updated_at"]


class MedicationRequestCategorySerializer(serializers.ModelSerializer):
    """medication request category serializer."""

    class Meta:
        """metadata."""

        model = MedicationRequestCategory
        exclude = ["created_at", "updated_at"]


class MedicationRequestMedicationCodeSerializer(serializers.ModelSerializer):
    """medication request medication code serializer."""

    class Meta:
        """metadata."""

        model = MedicationRequestMedicationCode
        exclude = ["created_at", "updated_at"]


class MediationRequestReferenceTypeSerializer(serializers.ModelSerializer):
    """medication request reference type serializer."""

    class Meta:
        """metadata."""

        model = MedicationRequestReferenceType
        exclude = ["created_at", "updated_at"]


class MedicationRequestReasonSerializer(serializers.ModelSerializer):
    """medication request reason serializer."""

    class Meta:
        """metadata."""

        model = MedicationRequestReason
        exclude = ["created_at", "updated_at"]


class AdditionalIllustrationSerializer(serializers.ModelSerializer):
    """additional illustration serializer."""

    class Meta:
        """metadata."""

        model = AdditionalIllustration
        exclude = ["created_at", "updated_at"]


class ReferenceAsNeededForSerializer(serializers.ModelSerializer):
    """reference as needed for serializer."""

    class Meta:
        """metadata."""

        model = ReferenceAsNeededFor
        exclude = ["created_at", "updated_at"]


class DosageSiteSerializer(serializers.ModelSerializer):
    """dosage site serializer."""

    class Meta:
        """metadata."""

        model = DosageSite
        exclude = ["created_at", "updated_at"]


class DosageRouteSerializer(serializers.ModelSerializer):
    """dosage route serializer."""

    class Meta:
        """metadata."""

        model = DosageRoute
        exclude = ["created_at", "updated_at"]


class DosageMethodSerializer(serializers.ModelSerializer):
    """dosage method serializer."""

    class Meta:
        """metadata."""

        model = DosageMethod
        exclude = ["created_at", "updated_at"]
