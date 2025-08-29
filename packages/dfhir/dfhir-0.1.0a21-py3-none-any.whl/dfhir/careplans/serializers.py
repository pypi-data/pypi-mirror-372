"""care plan serializers."""

from drf_writable_nested.serializers import WritableNestedModelSerializer

from dfhir.base.serializers import (
    AnnotationSerializer,
    BaseReferenceModelSerializer,
    BaseWritableNestedModelSerializer,
    CodeableConceptSerializer,
    CodeableReferenceSerializer,
    IdentifierSerializer,
    PeriodSerializer,
    ReferenceSerializer,
)
from dfhir.careteams.serializers import CareTeamReferenceSerializer
from dfhir.encounters.serializers import EncounterReferenceSerializer
from dfhir.patients.serializers import PatientGroupReferenceSerializer

from .models import (
    CarePlan,
    CarePlanActivity,
    CarePlanAddressesCodeableReference,
    CarePlanAddressReference,
    CarePlanBasedOnReference,
    CarePlanContributorReference,
    CarePlanCustodianReference,
    CarePlanDeviceRequestReference,
    CarePlanPlannedActivityReference,
    CarePlanReference,
)


class CarePlanBasedOnReferenceSerializer(BaseReferenceModelSerializer):
    """Care Plan Based On Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = CarePlanBasedOnReference
        exclude = ["created_at", "updated_at"]


class CarePlanContributorReferenceSerializer(BaseReferenceModelSerializer):
    """Care Plan Contributor Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = CarePlanContributorReference
        exclude = ["created_at", "updated_at"]


class CarePlanCustodianReferenceSerializer(BaseReferenceModelSerializer):
    """Care Plan Custodian Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = CarePlanCustodianReference
        exclude = ["created_at", "updated_at"]


class CarePlanAddressReferenceSerializer(BaseReferenceModelSerializer):
    """Care Plan Address Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = CarePlanAddressReference
        exclude = ["created_at", "updated_at"]


class CarePlanPlannedActivityReferenceSerializer(BaseReferenceModelSerializer):
    """Care Plan Planned Activity Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = CarePlanPlannedActivityReference
        exclude = ["created_at", "updated_at"]


class CarePlanActivitySerializer(WritableNestedModelSerializer):
    """Care Plan Activity Serializer."""

    performer_activity = CodeableReferenceSerializer(required=False, many=True)
    progress = AnnotationSerializer(required=False, many=True)
    planned_activity_reference = CarePlanPlannedActivityReferenceSerializer(
        required=False, many=False
    )

    class Meta:
        """Meta."""

        model = CarePlanActivity
        exclude = ["created_at", "updated_at"]


class CarePlanReferenceSerializer(BaseReferenceModelSerializer):
    """Care Plan Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = CarePlanReference
        exclude = ["created_at", "updated_at"]


class CarePlanAddressesCodeableReferenceSerializer(WritableNestedModelSerializer):
    """Care Plan Addresses Codeable Reference Serializer."""

    reference = CarePlanReferenceSerializer(required=False, many=False)
    concept = CodeableConceptSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = CarePlanAddressesCodeableReference
        exclude = ["created_at", "updated_at"]


class CarePlanSerializer(BaseWritableNestedModelSerializer):
    """care plan serializer."""

    identifier = IdentifierSerializer(many=True, required=False)
    based_on = CarePlanBasedOnReferenceSerializer(many=True, required=False)
    replaces = CarePlanReferenceSerializer(many=True, required=False)
    part_of = CarePlanReferenceSerializer(many=True, required=False)
    category = CodeableConceptSerializer(many=True, required=False)
    subject = PatientGroupReferenceSerializer(required=False, many=False)
    encounter = EncounterReferenceSerializer(required=False, many=False)
    period = PeriodSerializer(required=False, many=False)
    custodian = CarePlanCustodianReferenceSerializer(many=False, required=False)
    contributor = CarePlanContributorReferenceSerializer(many=True, required=False)
    care_team = CareTeamReferenceSerializer(many=True, required=False)
    addresses = CarePlanAddressesCodeableReferenceSerializer(many=True, required=False)
    supporting_info = ReferenceSerializer(many=True, required=False)
    activity = CarePlanActivitySerializer(many=True, required=False)
    goal = ReferenceSerializer(many=True, required=False)

    class Meta:
        """meta options."""

        model = CarePlan
        exclude = ["created_at", "updated_at"]


class CarePlanDeviceRequestReferenceSerializer(BaseReferenceModelSerializer):
    """Care Plan Device Request Reference Serializer."""

    identifier = IdentifierSerializer(required=False, many=False)

    class Meta:
        """Meta."""

        model = CarePlanDeviceRequestReference
        exclude = ["created_at", "updated_at"]
