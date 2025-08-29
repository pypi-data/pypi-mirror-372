"""immunization serializers."""

from drf_writable_nested import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    IdentifierSerializer,
    OrganizationReferenceSerializer,
    ReferenceSerializer,
    SimpleQuantitySerializer,
)
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.immunizations.models import (
    Immunization,
    ImmunizationBasedOnReference,
    ImmunizationInformationSourceRefrence,
    ImmunizationPerformer,
    ImmunizationPerformerActorReference,
    ImmunizationProgramEligibility,
    ImmunizationProtocolApplied,
    ImmunizationReaction,
    ImmunizationReasonCodeableReference,
    ImmunizationReasonReference,
    ImmunizationReference,
)
from dfhir.locations.serializers import LocationReferenceSerializer
from dfhir.medications.serializers import (
    MedicationCodeableReferenceSerializer,
)
from dfhir.observations.serializers import (
    ObservationCodeableReferenceSerializer,
)
from dfhir.organizations.serializers import OrganizationCodeableReferenceSerializer
from dfhir.patients.serializers import PatientReferenceSerializer


class ImmunizationReferenceSerializer(BaseReferenceModelSerializer):
    """immunization reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = ImmunizationReference
        exclude = ["created_at", "updated_at"]


class ImmunizationBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """ImmunizationBasedOn reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = ImmunizationBasedOnReference
        exclude = ["created_at", "updated_at"]


class ImmunizationInformationSourceRefrenceSerializer(BaseReferenceModelSerializer):
    """ImmunizationInformationSource reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = ImmunizationInformationSourceRefrence
        exclude = ["created_at", "updated_at"]


class ImmunizationPerformerActorReferenceSerializer(BaseReferenceModelSerializer):
    """ImmunizationPerformerActor reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = ImmunizationPerformerActorReference
        exclude = ["created_at", "updated_at"]


class ImmunizationPerformerSerializer(WritableNestedModelSerializer):
    """ImmunizationPerformer serializer."""

    function = CodeableConceptSerializer(required=False)
    actor = ImmunizationPerformerActorReferenceSerializer()

    class Meta:
        """Meta options."""

        model = ImmunizationPerformer
        exclude = ["created_at", "updated_at"]


class ImmunizationProgramEligibilitySerializer(WritableNestedModelSerializer):
    """Immunization Program Eligibility serializer."""

    program = CodeableConceptSerializer(required=False)
    program_status = CodeableConceptSerializer(required=False)

    class Meta:
        """Meta options."""

        model = ImmunizationProgramEligibility
        exclude = ["created_at", "updated_at"]


class ImmunizationProtocolAppliedSerializer(WritableNestedModelSerializer):
    """Immunization Protocol Applied serializer."""

    authority = OrganizationReferenceSerializer(required=False)
    usage_disease = CodeableConceptSerializer(many=True, required=False)

    class Meta:
        """Meta options."""

        model = ImmunizationProtocolApplied
        exclude = ["created_at", "updated_at"]


class ImmunizationReactionSerializer(WritableNestedModelSerializer):
    """Immunization Reaction serializer."""

    manifestation = ObservationCodeableReferenceSerializer(required=False)

    class Meta:
        """Meta options."""

        model = ImmunizationReaction
        exclude = ["created_at", "updated_at"]


class ImmunizationReasonReferenceSerializer(BaseReferenceModelSerializer):
    """ImmunizationReason reference serializer."""

    identifier = IdentifierSerializer(required=False)

    class Meta:
        """Meta options."""

        model = ImmunizationReasonReference
        exclude = ["created_at", "updated_at"]


class ImmunizationReasonCodeableReferenceSerializer(WritableNestedModelSerializer):
    """immunization reason codeable reference serializer."""

    concept = CodeableConceptSerializer(required=False)
    reference = ImmunizationReasonReferenceSerializer(required=False)

    class Meta:
        """Meta options."""

        model = ImmunizationReasonCodeableReference
        exclude = ["created_at", "updated_at"]


class ImmunizationSerializer(BaseWritableNestedModelSerializer):
    """Immunization serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = ImmunizationBasedOnReferenceSerializer(many=True, required=False)
    status_reason = CodeableConceptSerializer(many=False, required=False)
    vaccine_code = CodeableConceptSerializer(required=False)
    administered_product = MedicationCodeableReferenceSerializer(required=False)
    manufacturer = OrganizationCodeableReferenceSerializer(required=False)
    patient = PatientReferenceSerializer(required=False)
    encounter = EncounterReferenceSerializer(required=False)
    supporting_information = ReferenceSerializer(many=True, required=False)
    information_source = ImmunizationInformationSourceRefrenceSerializer(required=False)
    location = LocationReferenceSerializer(required=False)
    site = CodeableConceptSerializer(required=False)
    route = CodeableConceptSerializer(required=False)
    dose_quantity = SimpleQuantitySerializer(required=False)
    performer = ImmunizationPerformerSerializer(many=True, required=False)
    note = AnnotationSerializer(many=True, required=False)
    reason = ImmunizationReasonCodeableReferenceSerializer(many=True, required=False)
    sub_potent_reason = CodeableConceptSerializer(many=True, required=False)
    program_eligibility = ImmunizationProgramEligibilitySerializer(
        many=True, required=False
    )
    funding_source = CodeableConceptSerializer(required=False)
    reaction = ImmunizationReactionSerializer(many=True, required=False)
    protocol_applied = ImmunizationProtocolAppliedSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = Immunization
        exclude = ["created_at", "updated_at"]
